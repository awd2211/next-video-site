"""
订阅服务

处理订阅创建、取消、续费等核心业务逻辑
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.subscription import (
    SubscriptionPlan,
    UserSubscription,
    SubscriptionStatus,
    BillingPeriod,
)
from app.models.user import User
from app.models.coupon import Coupon
from app.schemas.subscription import (
    UserSubscriptionCreate,
    UserSubscriptionUpdate,
)
from app.services.payment_gateway import (
    PaymentGatewayFactory,
    PaymentGatewayConfig,
    PaymentGatewayException,
)
from app.models.payment import PaymentProvider


class SubscriptionService:
    """订阅服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_plan(self, plan_id: int) -> Optional[SubscriptionPlan]:
        """获取订阅套餐"""
        result = await self.db.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
        )
        return result.scalar_one_or_none()

    async def list_active_plans(self) -> List[SubscriptionPlan]:
        """获取所有激活的订阅套餐"""
        result = await self.db.execute(
            select(SubscriptionPlan)
            .where(SubscriptionPlan.is_active == True)
            .order_by(SubscriptionPlan.display_order, SubscriptionPlan.id)
        )
        return list(result.scalars().all())

    async def get_user_subscription(
        self, user_id: int, subscription_id: int
    ) -> Optional[UserSubscription]:
        """获取用户的订阅"""
        result = await self.db.execute(
            select(UserSubscription).where(
                and_(
                    UserSubscription.id == subscription_id,
                    UserSubscription.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_active_subscription(self, user_id: int) -> Optional[UserSubscription]:
        """获取用户当前激活的订阅"""
        result = await self.db.execute(
            select(UserSubscription)
            .where(
                and_(
                    UserSubscription.user_id == user_id,
                    UserSubscription.status == SubscriptionStatus.ACTIVE,
                    UserSubscription.end_date > datetime.now(),
                )
            )
            .order_by(UserSubscription.end_date.desc())
        )
        return result.scalar_one_or_none()

    async def create_subscription(
        self,
        user_id: int,
        subscription_data: UserSubscriptionCreate,
        provider: PaymentProvider,
        gateway_config: PaymentGatewayConfig,
    ) -> UserSubscription:
        """
        创建订阅

        Args:
            user_id: 用户ID
            subscription_data: 订阅数据
            provider: 支付提供商
            gateway_config: 支付网关配置

        Returns:
            UserSubscription: 新创建的订阅
        """
        # 检查是否已有激活订阅
        existing = await self.get_active_subscription(user_id)
        if existing:
            raise ValueError("User already has an active subscription")

        # 获取套餐
        plan = await self.get_plan(subscription_data.plan_id)
        if not plan:
            raise ValueError("Subscription plan not found")

        if not plan.is_active:
            raise ValueError("Subscription plan is not active")

        # 计算价格和折扣
        discount_amount = Decimal(0)
        coupon = None

        if subscription_data.coupon_code:
            coupon = await self._validate_coupon(
                subscription_data.coupon_code, plan.id, user_id
            )
            if coupon:
                discount_amount = await self._calculate_discount(coupon, plan.price_usd)

        # 创建支付网关实例
        gateway = PaymentGatewayFactory.create(gateway_config)

        # 获取用户
        user_result = await self.db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one()

        # 在支付网关创建客户 (如果还没有)
        provider_customer_id = await gateway.create_customer(
            email=user.email, name=user.full_name or user.username
        )

        # 计算订阅时间
        now = datetime.now()
        trial_end_date = None
        start_date = now

        if plan.trial_days > 0:
            trial_end_date = now + timedelta(days=plan.trial_days)

        end_date = self._calculate_end_date(now, plan.billing_period)

        # 在支付网关创建订阅
        try:
            gateway_subscription = await gateway.create_subscription(
                customer_id=provider_customer_id,
                price_id=f"price_{plan.id}",  # 需要在 Stripe/PayPal 中预先创建价格
                trial_days=plan.trial_days if plan.trial_days > 0 else None,
                metadata={"user_id": user_id, "plan_id": plan.id},
            )
        except PaymentGatewayException as e:
            raise ValueError(f"Failed to create subscription: {str(e)}")

        # 创建订阅记录
        subscription = UserSubscription(
            user_id=user_id,
            plan_id=plan.id,
            status=SubscriptionStatus.TRIALING
            if trial_end_date
            else SubscriptionStatus.ACTIVE,
            start_date=start_date,
            end_date=end_date,
            trial_end_date=trial_end_date,
            auto_renew=subscription_data.auto_renew,
            renew_at=end_date if subscription_data.auto_renew else None,
            payment_method_id=subscription_data.payment_method_id,
            coupon_id=coupon.id if coupon else None,
            discount_amount=discount_amount,
        )

        # 设置支付网关订阅ID
        if provider == PaymentProvider.STRIPE:
            subscription.stripe_subscription_id = gateway_subscription["subscription_id"]
        elif provider == PaymentProvider.PAYPAL:
            subscription.paypal_subscription_id = gateway_subscription["subscription_id"]

        self.db.add(subscription)

        # 如果使用了优惠券，增加使用次数
        if coupon:
            coupon.usage_count += 1

        await self.db.commit()
        await self.db.refresh(subscription)

        return subscription

    async def cancel_subscription(
        self,
        user_id: int,
        subscription_id: int,
        immediately: bool = False,
        provider: PaymentProvider = None,
        gateway_config: PaymentGatewayConfig = None,
    ) -> UserSubscription:
        """
        取消订阅

        Args:
            user_id: 用户ID
            subscription_id: 订阅ID
            immediately: 是否立即取消
            provider: 支付提供商
            gateway_config: 支付网关配置

        Returns:
            UserSubscription: 更新后的订阅
        """
        subscription = await self.get_user_subscription(user_id, subscription_id)
        if not subscription:
            raise ValueError("Subscription not found")

        if subscription.status in [
            SubscriptionStatus.CANCELED,
            SubscriptionStatus.EXPIRED,
        ]:
            raise ValueError("Subscription is already canceled or expired")

        # 在支付网关取消订阅
        if gateway_config and provider:
            gateway = PaymentGatewayFactory.create(gateway_config)

            # 获取对应的支付网关订阅ID
            gateway_subscription_id = None
            if provider == PaymentProvider.STRIPE:
                gateway_subscription_id = subscription.stripe_subscription_id
            elif provider == PaymentProvider.PAYPAL:
                gateway_subscription_id = subscription.paypal_subscription_id

            if gateway_subscription_id:
                try:
                    await gateway.cancel_subscription(
                        gateway_subscription_id, immediately=immediately
                    )
                except PaymentGatewayException as e:
                    # 记录错误但继续处理
                    print(f"Warning: Failed to cancel subscription in gateway: {e}")

        # 更新订阅状态
        subscription.canceled_at = datetime.now()
        subscription.auto_renew = False

        if immediately:
            subscription.status = SubscriptionStatus.CANCELED
            subscription.end_date = datetime.now()
        else:
            # 期末取消，继续有效直到结束日期
            subscription.status = SubscriptionStatus.ACTIVE

        await self.db.commit()
        await self.db.refresh(subscription)

        return subscription

    async def update_subscription(
        self, user_id: int, subscription_id: int, update_data: UserSubscriptionUpdate
    ) -> UserSubscription:
        """更新订阅"""
        subscription = await self.get_user_subscription(user_id, subscription_id)
        if not subscription:
            raise ValueError("Subscription not found")

        # 更新字段
        if update_data.auto_renew is not None:
            subscription.auto_renew = update_data.auto_renew
            if update_data.auto_renew and not subscription.renew_at:
                subscription.renew_at = subscription.end_date

        if update_data.payment_method_id is not None:
            subscription.payment_method_id = update_data.payment_method_id

        await self.db.commit()
        await self.db.refresh(subscription)

        return subscription

    async def renew_subscription(
        self, subscription_id: int, gateway_config: Optional[PaymentGatewayConfig] = None
    ) -> UserSubscription:
        """
        续费订阅

        由定时任务或 webhook 调用
        """
        result = await self.db.execute(
            select(UserSubscription).where(UserSubscription.id == subscription_id)
        )
        subscription = result.scalar_one_or_none()

        if not subscription:
            raise ValueError("Subscription not found")

        # 检查是否需要续费
        if not subscription.auto_renew:
            return subscription

        if datetime.now() < subscription.end_date:
            return subscription

        # 延长订阅时间
        old_end_date = subscription.end_date
        new_end_date = self._calculate_end_date(old_end_date, subscription.plan.billing_period)

        subscription.start_date = old_end_date
        subscription.end_date = new_end_date
        subscription.renew_at = new_end_date
        subscription.status = SubscriptionStatus.ACTIVE

        await self.db.commit()
        await self.db.refresh(subscription)

        return subscription

    async def _validate_coupon(
        self, code: str, plan_id: int, user_id: int
    ) -> Optional[Coupon]:
        """验证优惠券"""
        result = await self.db.execute(select(Coupon).where(Coupon.code == code))
        coupon = result.scalar_one_or_none()

        if not coupon:
            return None

        if not coupon.is_valid():
            return None

        # 检查是否适用于该套餐
        if coupon.applicable_plans:
            import json

            applicable_plan_ids = json.loads(coupon.applicable_plans)
            if plan_id not in applicable_plan_ids:
                return None

        # 检查是否仅限首次购买
        if coupon.is_first_purchase_only:
            # 检查用户是否有过订阅
            existing_result = await self.db.execute(
                select(UserSubscription).where(UserSubscription.user_id == user_id).limit(1)
            )
            if existing_result.scalar_one_or_none():
                return None

        return coupon

    async def _calculate_discount(self, coupon: Coupon, amount: Decimal) -> Decimal:
        """计算折扣金额"""
        from app.models.coupon import DiscountType

        if coupon.discount_type == DiscountType.PERCENTAGE:
            discount = amount * (coupon.discount_value / 100)
        elif coupon.discount_type == DiscountType.FIXED_AMOUNT:
            discount = coupon.discount_value
        else:
            discount = Decimal(0)

        # 应用最大折扣限制
        if coupon.max_discount_amount and discount > coupon.max_discount_amount:
            discount = coupon.max_discount_amount

        # 折扣不能超过原价
        if discount > amount:
            discount = amount

        return discount

    def _calculate_end_date(self, start_date: datetime, billing_period: BillingPeriod) -> datetime:
        """计算订阅结束日期"""
        if billing_period == BillingPeriod.MONTHLY:
            return start_date + timedelta(days=30)
        elif billing_period == BillingPeriod.QUARTERLY:
            return start_date + timedelta(days=90)
        elif billing_period == BillingPeriod.YEARLY:
            return start_date + timedelta(days=365)
        elif billing_period == BillingPeriod.LIFETIME:
            # 终身订阅，设置为100年后
            return start_date + timedelta(days=36500)
        else:
            return start_date + timedelta(days=30)
