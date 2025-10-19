"""
Stripe 支付网关实现

支持信用卡(Visa, Mastercard)、Apple Pay 等
"""

import stripe
from decimal import Decimal
from typing import Optional, Dict, Any
from datetime import datetime

from app.services.payment_gateway import (
    PaymentGateway,
    PaymentGatewayConfig,
    PaymentResult,
    RefundResult,
    PaymentGatewayException,
    PaymentGatewayFactory,
)
from app.models.payment import PaymentProvider, Currency


class StripeGateway(PaymentGateway):
    """Stripe 支付网关"""

    def __init__(self, config: PaymentGatewayConfig):
        super().__init__(config)
        # 初始化 Stripe
        stripe.api_key = config.api_key
        self.webhook_secret = config.webhook_secret

    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: Currency,
        customer_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PaymentResult:
        """创建 Stripe PaymentIntent"""
        try:
            # Stripe 金额以最小单位计算 (美元: 分, 日元: 円)
            amount_cents = self._to_stripe_amount(amount, currency)

            params = {
                "amount": amount_cents,
                "currency": currency.value.lower(),
                "description": description,
                "metadata": metadata or {},
            }

            if customer_id:
                params["customer"] = customer_id

            if payment_method_id:
                params["payment_method"] = payment_method_id
                params["confirm"] = True  # 自动确认支付

            payment_intent = stripe.PaymentIntent.create(**params)

            return PaymentResult(
                success=payment_intent.status in ["succeeded", "processing"],
                provider_payment_id=payment_intent.id,
                provider_customer_id=payment_intent.customer,
                amount=amount,
                currency=currency,
                status=payment_intent.status,
                receipt_url=payment_intent.charges.data[0].receipt_url if payment_intent.charges.data else None,
                metadata={"client_secret": payment_intent.client_secret},
            )

        except stripe.error.StripeError as e:
            return PaymentResult(
                success=False,
                failure_code=e.code,
                failure_message=str(e),
            )

    async def confirm_payment(
        self,
        payment_intent_id: str,
        payment_method_id: Optional[str] = None,
    ) -> PaymentResult:
        """确认 Stripe 支付"""
        try:
            params = {}
            if payment_method_id:
                params["payment_method"] = payment_method_id

            payment_intent = stripe.PaymentIntent.confirm(payment_intent_id, **params)

            return PaymentResult(
                success=payment_intent.status in ["succeeded", "processing"],
                provider_payment_id=payment_intent.id,
                provider_customer_id=payment_intent.customer,
                amount=Decimal(payment_intent.amount) / 100,  # 转换回美元
                currency=Currency(payment_intent.currency.upper()),
                status=payment_intent.status,
                receipt_url=payment_intent.charges.data[0].receipt_url if payment_intent.charges.data else None,
            )

        except stripe.error.StripeError as e:
            return PaymentResult(
                success=False,
                failure_code=e.code,
                failure_message=str(e),
            )

    async def get_payment_status(self, payment_id: str) -> PaymentResult:
        """查询 Stripe 支付状态"""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_id)

            return PaymentResult(
                success=payment_intent.status in ["succeeded", "processing"],
                provider_payment_id=payment_intent.id,
                provider_customer_id=payment_intent.customer,
                amount=self._from_stripe_amount(payment_intent.amount, payment_intent.currency),
                currency=Currency(payment_intent.currency.upper()),
                status=payment_intent.status,
                receipt_url=payment_intent.charges.data[0].receipt_url if payment_intent.charges.data else None,
            )

        except stripe.error.StripeError as e:
            raise PaymentGatewayException(f"Failed to get payment status: {e}")

    async def create_refund(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None,
    ) -> RefundResult:
        """创建 Stripe 退款"""
        try:
            params = {"payment_intent": payment_id}

            if amount:
                # 获取原支付的货币
                payment_intent = stripe.PaymentIntent.retrieve(payment_id)
                params["amount"] = self._to_stripe_amount(amount, Currency(payment_intent.currency.upper()))

            if reason:
                params["reason"] = reason

            refund = stripe.Refund.create(**params)

            return RefundResult(
                success=refund.status == "succeeded",
                refund_id=refund.id,
                amount=self._from_stripe_amount(refund.amount, refund.currency),
                refunded_at=datetime.fromtimestamp(refund.created) if refund.created else None,
            )

        except stripe.error.StripeError as e:
            return RefundResult(
                success=False,
                failure_message=str(e),
            )

    async def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """创建 Stripe 客户"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {},
            )
            return customer.id

        except stripe.error.StripeError as e:
            raise PaymentGatewayException(f"Failed to create customer: {e}")

    async def attach_payment_method(
        self,
        customer_id: str,
        payment_method_id: str,
    ) -> bool:
        """关联支付方式到 Stripe 客户"""
        try:
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id,
            )
            return True

        except stripe.error.StripeError as e:
            raise PaymentGatewayException(f"Failed to attach payment method: {e}")

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """创建 Stripe 订阅"""
        try:
            params = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "metadata": metadata or {},
                "payment_behavior": "default_incomplete",
                "expand": ["latest_invoice.payment_intent"],
            }

            if trial_days:
                params["trial_period_days"] = trial_days

            subscription = stripe.Subscription.create(**params)

            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_start": datetime.fromtimestamp(subscription.current_period_start),
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end),
                "trial_end": datetime.fromtimestamp(subscription.trial_end) if subscription.trial_end else None,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret
                if subscription.latest_invoice and subscription.latest_invoice.payment_intent
                else None,
            }

        except stripe.error.StripeError as e:
            raise PaymentGatewayException(f"Failed to create subscription: {e}")

    async def cancel_subscription(
        self,
        subscription_id: str,
        immediately: bool = False,
    ) -> bool:
        """取消 Stripe 订阅"""
        try:
            if immediately:
                stripe.Subscription.delete(subscription_id)
            else:
                # 期末取消
                stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True,
                )
            return True

        except stripe.error.StripeError as e:
            raise PaymentGatewayException(f"Failed to cancel subscription: {e}")

    async def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
    ) -> bool:
        """验证 Stripe webhook 签名"""
        try:
            stripe.Webhook.construct_event(
                payload,
                signature,
                self.webhook_secret,
            )
            return True

        except (stripe.error.SignatureVerificationError, ValueError):
            return False

    def _to_stripe_amount(self, amount: Decimal, currency: Currency) -> int:
        """
        转换金额为 Stripe 格式

        大多数货币使用最小单位 (如美元的分)
        零小数货币 (如日元) 直接使用整数
        """
        # 零小数货币列表
        zero_decimal_currencies = ["JPY", "KRW", "VND", "CLP"]

        if currency.value in zero_decimal_currencies:
            return int(amount)
        else:
            return int(amount * 100)

    def _from_stripe_amount(self, amount: int, currency: str) -> Decimal:
        """从 Stripe 格式转换金额"""
        zero_decimal_currencies = ["JPY", "KRW", "VND", "CLP"]

        if currency.upper() in zero_decimal_currencies:
            return Decimal(amount)
        else:
            return Decimal(amount) / 100


# 注册到工厂
PaymentGatewayFactory.register(PaymentProvider.STRIPE, StripeGateway)
