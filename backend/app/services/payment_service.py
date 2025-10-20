"""
支付服务

处理支付创建、确认、退款等核心业务逻辑
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.models.payment import (
    Payment,
    PaymentMethod,
    PaymentProvider,
    PaymentStatus,
    PaymentType,
    Currency,
)
from app.models.user import User
from app.schemas.payment import PaymentIntentRequest, PaymentConfirmRequest, RefundRequestCreate
from app.services.payment_gateway import (
    PaymentGateway,
    PaymentGatewayFactory,
    PaymentGatewayConfig,
    PaymentGatewayException,
    PaymentResult,
    RefundResult,
)


class PaymentService:
    """支付服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payment_intent(
        self,
        user_id: int,
        request: PaymentIntentRequest,
        gateway_config: PaymentGatewayConfig,
    ) -> Dict[str, Any]:
        """
        创建支付意图

        Args:
            user_id: 用户ID
            request: 支付请求
            gateway_config: 支付网关配置

        Returns:
            Dict: 包含支付信息的字典
        """
        # 获取用户
        user_result = await self.db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one()

        # 创建支付网关
        gateway = PaymentGatewayFactory.create(gateway_config)

        # 获取或创建支付网关客户
        provider_customer_id = None
        if request.payment_method_id:
            # 如果提供了支付方式，获取关联的客户ID
            # 这里简化处理，实际应该从 PaymentMethod 表查询
            provider_customer_id = f"cus_{user_id}"
        else:
            # 创建新客户
            try:
                provider_customer_id = await gateway.create_customer(
                    email=user.email, name=user.full_name or user.username
                )
            except PaymentGatewayException as e:
                raise ValueError(f"Failed to create customer: {str(e)}")

        # 在支付网关创建支付意图
        try:
            payment_result: PaymentResult = await gateway.create_payment_intent(
                amount=request.amount,
                currency=request.currency,
                customer_id=provider_customer_id,
                payment_method_id=request.payment_method_id,
                description=request.description,
                metadata={"user_id": user_id},
            )
        except PaymentGatewayException as e:
            raise ValueError(f"Failed to create payment intent: {str(e)}")

        if not payment_result.success:
            raise ValueError(
                payment_result.failure_message or "Failed to create payment intent"
            )

        # 创建支付记录
        payment = Payment(
            user_id=user_id,
            provider=request.provider,
            provider_payment_id=payment_result.provider_payment_id,
            provider_customer_id=payment_result.provider_customer_id,
            amount=request.amount,
            currency=request.currency,
            status=PaymentStatus.PENDING,
            payment_type=PaymentType.ONE_TIME,
            description=request.description,
        )

        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)

        return {
            "payment_id": payment.id,
            "provider_payment_id": payment_result.provider_payment_id,
            "client_secret": payment_result.metadata.get("client_secret"),
            "payment_url": payment_result.metadata.get("payment_url"),
            "status": payment_result.status,
        }

    async def confirm_payment(
        self, user_id: int, request: PaymentConfirmRequest, gateway_config: PaymentGatewayConfig
    ) -> Payment:
        """
        确认支付

        Args:
            user_id: 用户ID
            request: 确认请求
            gateway_config: 支付网关配置

        Returns:
            Payment: 更新后的支付记录
        """
        # 获取支付记录
        payment = await self.get_payment(user_id, request.payment_id)
        if not payment:
            raise ValueError("Payment not found")

        if payment.status == PaymentStatus.SUCCEEDED:
            return payment

        # 创建支付网关
        gateway = PaymentGatewayFactory.create(gateway_config)

        # 确认支付
        try:
            payment_result: PaymentResult = await gateway.confirm_payment(
                payment_intent_id=payment.provider_payment_id,
                payment_method_id=request.payment_method_id,
            )
        except PaymentGatewayException as e:
            payment.status = PaymentStatus.FAILED
            payment.failure_code = "gateway_error"
            payment.failure_message = str(e)
            await self.db.commit()
            raise ValueError(f"Failed to confirm payment: {str(e)}")

        # 更新支付记录
        if payment_result.success:
            payment.status = PaymentStatus.SUCCEEDED
            payment.paid_at = datetime.now()
            payment.receipt_url = payment_result.receipt_url
        else:
            payment.status = PaymentStatus.FAILED
            payment.failure_code = payment_result.failure_code
            payment.failure_message = payment_result.failure_message

        await self.db.commit()
        await self.db.refresh(payment)

        return payment

    async def create_refund(
        self, user_id: int, request: RefundRequestCreate, gateway_config: PaymentGatewayConfig
    ) -> Dict[str, Any]:
        """
        创建退款

        Args:
            user_id: 用户ID (管理员可为空)
            request: 退款请求
            gateway_config: 支付网关配置

        Returns:
            Dict: 退款结果
        """
        # 获取支付记录
        result = await self.db.execute(
            select(Payment).where(Payment.id == request.payment_id)
        )
        payment = result.scalar_one_or_none()

        if not payment:
            raise ValueError("Payment not found")

        # 检查权限 (如果提供了 user_id)
        if user_id and payment.user_id != user_id:
            raise ValueError("Payment does not belong to user")

        if payment.status != PaymentStatus.SUCCEEDED:
            raise ValueError("Can only refund succeeded payments")

        # 检查退款金额
        refund_amount = request.amount if request.amount else payment.amount

        if refund_amount > (payment.amount - payment.refund_amount):
            raise ValueError("Refund amount exceeds remaining amount")

        # 创建支付网关
        gateway = PaymentGatewayFactory.create(gateway_config)

        # 创建退款
        try:
            refund_result: RefundResult = await gateway.create_refund(
                payment_id=payment.provider_payment_id,
                amount=refund_amount,
                reason=request.reason,
            )
        except PaymentGatewayException as e:
            raise ValueError(f"Failed to create refund: {str(e)}")

        if not refund_result.success:
            raise ValueError(refund_result.failure_message or "Failed to create refund")

        # 更新支付记录
        payment.refund_amount += refund_amount
        payment.refund_reason = request.reason
        payment.refunded_at = refund_result.refunded_at or datetime.now()

        # 更新状态
        if payment.refund_amount >= payment.amount:
            payment.status = PaymentStatus.REFUNDED
        else:
            payment.status = PaymentStatus.PARTIALLY_REFUNDED

        await self.db.commit()
        await self.db.refresh(payment)

        return {
            "success": True,
            "refund_id": refund_result.refund_id,
            "amount": refund_amount,
            "total_refunded": payment.refund_amount,
            "payment_status": payment.status.value,
        }

    async def get_payment(self, user_id: int, payment_id: int) -> Optional[Payment]:
        """获取支付记录"""
        result = await self.db.execute(
            select(Payment).where(
                and_(Payment.id == payment_id, Payment.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def list_user_payments(
        self, user_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[List[Payment], int]:
        """获取用户的支付记录列表"""
        # 查询总数
        count_result = await self.db.execute(
            select(Payment).where(Payment.user_id == user_id)
        )
        total = len(list(count_result.scalars().all()))

        # 查询列表
        result = await self.db.execute(
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(desc(Payment.created_at))
            .offset(skip)
            .limit(limit)
        )
        payments = list(result.scalars().all())

        return payments, total

    async def add_payment_method(
        self,
        user_id: int,
        provider: PaymentProvider,
        provider_payment_method_id: str,
        card_info: Optional[Dict[str, Any]] = None,
        is_default: bool = False,
    ) -> PaymentMethod:
        """
        添加支付方式

        Args:
            user_id: 用户ID
            provider: 支付提供商
            provider_payment_method_id: 支付网关的支付方式ID
            card_info: 卡信息 (仅用于显示)
            is_default: 是否设为默认

        Returns:
            PaymentMethod: 新创建的支付方式
        """
        # 如果设为默认，取消其他默认支付方式
        if is_default:
            result = await self.db.execute(
                select(PaymentMethod).where(
                    and_(
                        PaymentMethod.user_id == user_id,
                        PaymentMethod.is_default == True,
                    )
                )
            )
            for pm in result.scalars().all():
                pm.is_default = False

        # 创建支付方式
        payment_method = PaymentMethod(
            user_id=user_id,
            provider=provider,
            provider_payment_method_id=provider_payment_method_id,
            type=card_info.get("type", "card") if card_info else "card",
            card_brand=card_info.get("brand") if card_info else None,
            card_last4=card_info.get("last4") if card_info else None,
            card_exp_month=card_info.get("exp_month") if card_info else None,
            card_exp_year=card_info.get("exp_year") if card_info else None,
            is_default=is_default,
            is_active=True,
        )

        self.db.add(payment_method)
        await self.db.commit()
        await self.db.refresh(payment_method)

        return payment_method

    async def get_payment_method(
        self, user_id: int, payment_method_id: int
    ) -> Optional[PaymentMethod]:
        """获取支付方式"""
        result = await self.db.execute(
            select(PaymentMethod).where(
                and_(
                    PaymentMethod.id == payment_method_id,
                    PaymentMethod.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_payment_methods(self, user_id: int) -> List[PaymentMethod]:
        """获取用户的支付方式列表"""
        result = await self.db.execute(
            select(PaymentMethod)
            .where(
                and_(
                    PaymentMethod.user_id == user_id, PaymentMethod.is_active == True
                )
            )
            .order_by(desc(PaymentMethod.is_default), desc(PaymentMethod.created_at))
        )
        return list(result.scalars().all())

    async def set_default_payment_method(
        self, user_id: int, payment_method_id: int
    ) -> PaymentMethod:
        """设置默认支付方式"""
        # 获取支付方式
        payment_method = await self.get_payment_method(user_id, payment_method_id)
        if not payment_method:
            raise ValueError("Payment method not found")

        # 取消其他默认支付方式
        result = await self.db.execute(
            select(PaymentMethod).where(
                and_(PaymentMethod.user_id == user_id, PaymentMethod.is_default == True)
            )
        )
        for pm in result.scalars().all():
            pm.is_default = False

        # 设为默认
        payment_method.is_default = True

        await self.db.commit()
        await self.db.refresh(payment_method)

        return payment_method

    async def delete_payment_method(
        self, user_id: int, payment_method_id: int
    ) -> bool:
        """删除支付方式 (软删除)"""
        payment_method = await self.get_payment_method(user_id, payment_method_id)
        if not payment_method:
            raise ValueError("Payment method not found")

        payment_method.is_active = False

        await self.db.commit()

        return True

    async def handle_webhook(
        self, provider: PaymentProvider, payload: bytes, signature: str, gateway_config: PaymentGatewayConfig
    ) -> Dict[str, Any]:
        """
        处理支付网关 webhook

        Args:
            provider: 支付提供商
            payload: webhook 请求体
            signature: webhook 签名
            gateway_config: 支付网关配置

        Returns:
            Dict: 处理结果
        """
        # 创建支付网关
        gateway = PaymentGatewayFactory.create(gateway_config)

        # 验证签名
        is_valid = await gateway.verify_webhook_signature(payload, signature)
        if not is_valid:
            raise ValueError("Invalid webhook signature")

        # 解析 webhook 事件
        # 这里需要根据不同的支付网关解析事件
        # 简化处理，实际应该解析 JSON 并根据事件类型处理

        return {"success": True, "message": "Webhook processed"}
