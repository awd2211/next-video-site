"""
优惠券服务

处理优惠券验证、使用统计等业务逻辑
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc

from app.models.coupon import Coupon, CouponStatus, DiscountType
from app.models.subscription import UserSubscription
from app.schemas.coupon import CouponCreate, CouponUpdate


class CouponService:
    """优惠券服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_coupon(self, coupon_data: CouponCreate, admin_id: int) -> Coupon:
        """
        创建优惠券 (管理员)

        Args:
            coupon_data: 优惠券数据
            admin_id: 创建者ID

        Returns:
            Coupon: 新创建的优惠券
        """
        # 检查代码是否已存在
        existing_result = await self.db.execute(
            select(Coupon).where(Coupon.code == coupon_data.code)
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            raise ValueError("Coupon code already exists")

        # 创建优惠券
        coupon = Coupon(
            code=coupon_data.code.upper(),  # 统一大写
            discount_type=coupon_data.discount_type,
            discount_value=coupon_data.discount_value,
            max_discount_amount=coupon_data.max_discount_amount,
            usage_limit=coupon_data.usage_limit,
            usage_count=0,
            usage_limit_per_user=coupon_data.usage_limit_per_user,
            minimum_amount=coupon_data.minimum_amount,
            applicable_plans=coupon_data.applicable_plans,
            valid_from=coupon_data.valid_from,
            valid_until=coupon_data.valid_until,
            status=coupon_data.status,
            is_first_purchase_only=coupon_data.is_first_purchase_only,
            description=coupon_data.description,
            created_by=admin_id,
        )

        self.db.add(coupon)
        await self.db.commit()
        await self.db.refresh(coupon)

        return coupon

    async def get_coupon(self, coupon_id: int) -> Optional[Coupon]:
        """获取优惠券"""
        result = await self.db.execute(select(Coupon).where(Coupon.id == coupon_id))
        return result.scalar_one_or_none()

    async def get_coupon_by_code(self, code: str) -> Optional[Coupon]:
        """根据代码获取优惠券"""
        result = await self.db.execute(
            select(Coupon).where(Coupon.code == code.upper())
        )
        return result.scalar_one_or_none()

    async def list_coupons(
        self,
        status: Optional[CouponStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Coupon], int]:
        """获取优惠券列表"""
        query = select(Coupon)

        if status:
            query = query.where(Coupon.status == status)

        # 查询总数
        count_result = await self.db.execute(query)
        total = len(list(count_result.scalars().all()))

        # 查询列表
        result = await self.db.execute(
            query.order_by(desc(Coupon.created_at)).offset(skip).limit(limit)
        )
        coupons = list(result.scalars().all())

        return coupons, total

    async def update_coupon(
        self, coupon_id: int, update_data: CouponUpdate
    ) -> Coupon:
        """更新优惠券"""
        coupon = await self.get_coupon(coupon_id)
        if not coupon:
            raise ValueError("Coupon not found")

        # 更新字段
        if update_data.code is not None:
            # 检查新代码是否已存在
            existing_result = await self.db.execute(
                select(Coupon).where(
                    and_(
                        Coupon.code == update_data.code.upper(),
                        Coupon.id != coupon_id,
                    )
                )
            )
            if existing_result.scalar_one_or_none():
                raise ValueError("Coupon code already exists")

            coupon.code = update_data.code.upper()

        if update_data.discount_type is not None:
            coupon.discount_type = update_data.discount_type

        if update_data.discount_value is not None:
            coupon.discount_value = update_data.discount_value

        if update_data.max_discount_amount is not None:
            coupon.max_discount_amount = update_data.max_discount_amount

        if update_data.usage_limit is not None:
            coupon.usage_limit = update_data.usage_limit

        if update_data.usage_limit_per_user is not None:
            coupon.usage_limit_per_user = update_data.usage_limit_per_user

        if update_data.minimum_amount is not None:
            coupon.minimum_amount = update_data.minimum_amount

        if update_data.applicable_plans is not None:
            coupon.applicable_plans = update_data.applicable_plans

        if update_data.valid_from is not None:
            coupon.valid_from = update_data.valid_from

        if update_data.valid_until is not None:
            coupon.valid_until = update_data.valid_until

        if update_data.status is not None:
            coupon.status = update_data.status

        if update_data.is_first_purchase_only is not None:
            coupon.is_first_purchase_only = update_data.is_first_purchase_only

        if update_data.description is not None:
            coupon.description = update_data.description

        await self.db.commit()
        await self.db.refresh(coupon)

        return coupon

    async def validate_coupon(
        self, code: str, user_id: int, plan_id: int, amount: Decimal
    ) -> dict:
        """
        验证优惠券

        Args:
            code: 优惠券代码
            user_id: 用户ID
            plan_id: 套餐ID
            amount: 订单金额

        Returns:
            dict: 验证结果和折扣信息
        """
        # 获取优惠券
        coupon = await self.get_coupon_by_code(code)

        if not coupon:
            return {
                "valid": False,
                "error_message": "Coupon not found",
                "discount_amount": Decimal(0),
                "final_amount": amount,
            }

        # 基础验证
        if not coupon.is_valid():
            return {
                "valid": False,
                "error_message": "Coupon is not valid or expired",
                "discount_amount": Decimal(0),
                "final_amount": amount,
            }

        # 检查最低消费金额
        if coupon.minimum_amount and amount < coupon.minimum_amount:
            return {
                "valid": False,
                "error_message": f"Minimum amount {coupon.minimum_amount} required",
                "discount_amount": Decimal(0),
                "final_amount": amount,
            }

        # 检查适用套餐
        if coupon.applicable_plans:
            try:
                applicable_plan_ids = json.loads(coupon.applicable_plans)
                if plan_id not in applicable_plan_ids:
                    return {
                        "valid": False,
                        "error_message": "Coupon not applicable to this plan",
                        "discount_amount": Decimal(0),
                        "final_amount": amount,
                    }
            except json.JSONDecodeError:
                pass

        # 检查是否仅限首次购买
        if coupon.is_first_purchase_only:
            existing_result = await self.db.execute(
                select(UserSubscription)
                .where(UserSubscription.user_id == user_id)
                .limit(1)
            )
            if existing_result.scalar_one_or_none():
                return {
                    "valid": False,
                    "error_message": "Coupon is only for first purchase",
                    "discount_amount": Decimal(0),
                    "final_amount": amount,
                }

        # 检查每用户使用次数限制
        user_usage_result = await self.db.execute(
            select(UserSubscription).where(
                and_(
                    UserSubscription.user_id == user_id,
                    UserSubscription.coupon_id == coupon.id,
                )
            )
        )
        user_usage_count = len(list(user_usage_result.scalars().all()))

        if user_usage_count >= coupon.usage_limit_per_user:
            return {
                "valid": False,
                "error_message": f"You have reached the usage limit for this coupon",
                "discount_amount": Decimal(0),
                "final_amount": amount,
            }

        # 计算折扣
        discount_amount = self._calculate_discount(coupon, amount)
        final_amount = max(amount - discount_amount, Decimal(0))

        return {
            "valid": True,
            "coupon": coupon,
            "discount_amount": discount_amount,
            "final_amount": final_amount,
        }

    def _calculate_discount(self, coupon: Coupon, amount: Decimal) -> Decimal:
        """计算折扣金额"""
        if coupon.discount_type == DiscountType.PERCENTAGE:
            discount = amount * (coupon.discount_value / 100)
        elif coupon.discount_type == DiscountType.FIXED_AMOUNT:
            discount = coupon.discount_value
        else:
            # FREE_TRIAL 类型不影响金额
            discount = Decimal(0)

        # 应用最大折扣限制
        if coupon.max_discount_amount and discount > coupon.max_discount_amount:
            discount = coupon.max_discount_amount

        # 折扣不能超过原价
        if discount > amount:
            discount = amount

        return discount

    async def deactivate_coupon(self, coupon_id: int) -> Coupon:
        """停用优惠券"""
        coupon = await self.get_coupon(coupon_id)
        if not coupon:
            raise ValueError("Coupon not found")

        coupon.status = CouponStatus.DISABLED

        await self.db.commit()
        await self.db.refresh(coupon)

        return coupon

    async def activate_coupon(self, coupon_id: int) -> Coupon:
        """激活优惠券"""
        coupon = await self.get_coupon(coupon_id)
        if not coupon:
            raise ValueError("Coupon not found")

        coupon.status = CouponStatus.ACTIVE

        await self.db.commit()
        await self.db.refresh(coupon)

        return coupon

    async def get_coupon_statistics(self, coupon_id: int) -> dict:
        """
        获取优惠券统计数据

        Args:
            coupon_id: 优惠券ID

        Returns:
            dict: 统计数据
        """
        coupon = await self.get_coupon(coupon_id)
        if not coupon:
            raise ValueError("Coupon not found")

        # 查询使用记录
        usage_result = await self.db.execute(
            select(UserSubscription).where(UserSubscription.coupon_id == coupon_id)
        )
        usages = list(usage_result.scalars().all())

        total_discount = sum(usage.discount_amount for usage in usages)
        unique_users = len(set(usage.user_id for usage in usages))

        return {
            "coupon_code": coupon.code,
            "total_usage": coupon.usage_count,
            "usage_limit": coupon.usage_limit,
            "unique_users": unique_users,
            "total_discount_amount": float(total_discount),
            "average_discount": (
                float(total_discount / len(usages)) if usages else 0
            ),
            "is_valid": coupon.is_valid(),
            "status": coupon.status.value,
        }

    async def get_user_available_coupons(
        self, user_id: int, plan_id: Optional[int] = None
    ) -> List[Coupon]:
        """
        获取用户可用的优惠券

        Args:
            user_id: 用户ID
            plan_id: 套餐ID (可选)

        Returns:
            List[Coupon]: 可用优惠券列表
        """
        # 查询所有激活的优惠券
        result = await self.db.execute(
            select(Coupon).where(
                and_(
                    Coupon.status == CouponStatus.ACTIVE,
                    Coupon.valid_from <= datetime.now(),
                    or_(
                        Coupon.valid_until.is_(None),
                        Coupon.valid_until >= datetime.now(),
                    ),
                )
            )
        )
        all_coupons = list(result.scalars().all())

        available_coupons = []

        for coupon in all_coupons:
            # 检查使用次数限制
            if coupon.usage_limit and coupon.usage_count >= coupon.usage_limit:
                continue

            # 检查适用套餐
            if plan_id and coupon.applicable_plans:
                try:
                    applicable_plan_ids = json.loads(coupon.applicable_plans)
                    if plan_id not in applicable_plan_ids:
                        continue
                except json.JSONDecodeError:
                    pass

            # 检查是否仅限首次购买
            if coupon.is_first_purchase_only:
                existing_result = await self.db.execute(
                    select(UserSubscription)
                    .where(UserSubscription.user_id == user_id)
                    .limit(1)
                )
                if existing_result.scalar_one_or_none():
                    continue

            # 检查每用户使用次数
            user_usage_result = await self.db.execute(
                select(UserSubscription).where(
                    and_(
                        UserSubscription.user_id == user_id,
                        UserSubscription.coupon_id == coupon.id,
                    )
                )
            )
            user_usage_count = len(list(user_usage_result.scalars().all()))

            if user_usage_count >= coupon.usage_limit_per_user:
                continue

            available_coupons.append(coupon)

        return available_coupons
