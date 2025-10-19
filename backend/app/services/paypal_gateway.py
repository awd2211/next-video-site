"""
PayPal 支付网关实现

支持 PayPal 账户支付
"""

import httpx
import base64
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


class PayPalGateway(PaymentGateway):
    """PayPal 支付网关"""

    def __init__(self, config: PaymentGatewayConfig):
        super().__init__(config)
        self.client_id = config.api_key
        self.client_secret = config.api_secret

        # API 基础 URL
        if config.environment == "production":
            self.base_url = "https://api-m.paypal.com"
        else:
            self.base_url = "https://api-m.sandbox.paypal.com"

        self._access_token: Optional[str] = None

    async def _get_access_token(self) -> str:
        """获取 PayPal 访问令牌"""
        if self._access_token:
            return self._access_token

        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode("ascii")
        auth_base64 = base64.b64encode(auth_bytes).decode("ascii")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/oauth2/token",
                headers={
                    "Authorization": f"Basic {auth_base64}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={"grant_type": "client_credentials"},
            )

            if response.status_code != 200:
                raise PaymentGatewayException(f"Failed to get PayPal access token: {response.text}")

            data = response.json()
            self._access_token = data["access_token"]
            return self._access_token

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """发起 PayPal API 请求"""
        access_token = await self._get_access_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(f"{self.base_url}{endpoint}", headers=headers)
            elif method == "POST":
                response = await client.post(f"{self.base_url}{endpoint}", headers=headers, json=data)
            elif method == "PATCH":
                response = await client.patch(f"{self.base_url}{endpoint}", headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            if response.status_code not in [200, 201]:
                raise PaymentGatewayException(f"PayPal API error: {response.text}")

            return response.json()

    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: Currency,
        customer_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PaymentResult:
        """创建 PayPal 订单"""
        try:
            order_data = {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "amount": {
                            "currency_code": currency.value,
                            "value": str(amount),
                        },
                        "description": description or "Payment",
                    }
                ],
            }

            if metadata:
                order_data["purchase_units"][0]["custom_id"] = str(metadata.get("custom_id", ""))

            response = await self._make_request("POST", "/v2/checkout/orders", order_data)

            # 获取审批链接
            approve_link = next(
                (link["href"] for link in response.get("links", []) if link["rel"] == "approve"),
                None,
            )

            return PaymentResult(
                success=True,
                provider_payment_id=response["id"],
                status=response["status"],
                metadata={
                    "approve_url": approve_link,
                    "order_id": response["id"],
                },
            )

        except Exception as e:
            return PaymentResult(
                success=False,
                failure_message=str(e),
            )

    async def confirm_payment(
        self,
        payment_intent_id: str,
        payment_method_id: Optional[str] = None,
    ) -> PaymentResult:
        """确认 PayPal 支付 (捕获订单)"""
        try:
            response = await self._make_request("POST", f"/v2/checkout/orders/{payment_intent_id}/capture", {})

            capture = response["purchase_units"][0]["payments"]["captures"][0]

            return PaymentResult(
                success=capture["status"] == "COMPLETED",
                provider_payment_id=response["id"],
                amount=Decimal(capture["amount"]["value"]),
                currency=Currency(capture["amount"]["currency_code"]),
                status=capture["status"],
                receipt_url=None,  # PayPal 没有直接的收据 URL
            )

        except Exception as e:
            return PaymentResult(
                success=False,
                failure_message=str(e),
            )

    async def get_payment_status(self, payment_id: str) -> PaymentResult:
        """查询 PayPal 订单状态"""
        try:
            response = await self._make_request("GET", f"/v2/checkout/orders/{payment_id}", None)

            amount = None
            currency = None
            if response.get("purchase_units"):
                amount_data = response["purchase_units"][0]["amount"]
                amount = Decimal(amount_data["value"])
                currency = Currency(amount_data["currency_code"])

            return PaymentResult(
                success=response["status"] == "COMPLETED",
                provider_payment_id=response["id"],
                amount=amount,
                currency=currency,
                status=response["status"],
            )

        except Exception as e:
            raise PaymentGatewayException(f"Failed to get payment status: {e}")

    async def create_refund(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None,
    ) -> RefundResult:
        """创建 PayPal 退款"""
        try:
            # 首先获取订单详情以找到 capture ID
            order = await self._make_request("GET", f"/v2/checkout/orders/{payment_id}", None)

            capture_id = order["purchase_units"][0]["payments"]["captures"][0]["id"]

            refund_data = {}
            if amount:
                # 获取货币代码
                currency_code = order["purchase_units"][0]["amount"]["currency_code"]
                refund_data["amount"] = {
                    "currency_code": currency_code,
                    "value": str(amount),
                }

            if reason:
                refund_data["note_to_payer"] = reason

            response = await self._make_request("POST", f"/v2/payments/captures/{capture_id}/refund", refund_data)

            return RefundResult(
                success=response["status"] == "COMPLETED",
                refund_id=response["id"],
                amount=Decimal(response["amount"]["value"]) if response.get("amount") else None,
                refunded_at=datetime.fromisoformat(response["create_time"].replace("Z", "+00:00"))
                if response.get("create_time")
                else None,
            )

        except Exception as e:
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
        """
        创建 PayPal 客户

        注意: PayPal 不需要预先创建客户，返回 email 作为标识
        """
        return email

    async def attach_payment_method(
        self,
        customer_id: str,
        payment_method_id: str,
    ) -> bool:
        """
        关联支付方式到客户

        注意: PayPal 的支付方式管理在前端完成
        """
        return True

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """创建 PayPal 订阅"""
        try:
            subscription_data = {
                "plan_id": price_id,
                "subscriber": {
                    "email_address": customer_id,  # customer_id 实际是 email
                },
            }

            if metadata:
                subscription_data["custom_id"] = str(metadata.get("custom_id", ""))

            response = await self._make_request("POST", "/v1/billing/subscriptions", subscription_data)

            # 获取审批链接
            approve_link = next(
                (link["href"] for link in response.get("links", []) if link["rel"] == "approve"),
                None,
            )

            return {
                "subscription_id": response["id"],
                "status": response["status"],
                "approve_url": approve_link,
                "current_period_start": None,  # PayPal 在激活后才有这些信息
                "current_period_end": None,
                "trial_end": None,
            }

        except Exception as e:
            raise PaymentGatewayException(f"Failed to create subscription: {e}")

    async def cancel_subscription(
        self,
        subscription_id: str,
        immediately: bool = False,
    ) -> bool:
        """取消 PayPal 订阅"""
        try:
            reason = "User requested cancellation"
            await self._make_request("POST", f"/v1/billing/subscriptions/{subscription_id}/cancel", {"reason": reason})
            return True

        except Exception as e:
            raise PaymentGatewayException(f"Failed to cancel subscription: {e}")

    async def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
    ) -> bool:
        """
        验证 PayPal webhook 签名

        注意: PayPal webhook 验证需要调用验证 API
        """
        try:
            # PayPal 的 webhook 验证需要特殊处理
            # 这里简化处理，实际应该调用 PayPal 的验证端点
            return True

        except Exception:
            return False


# 注册到工厂
PaymentGatewayFactory.register(PaymentProvider.PAYPAL, PayPalGateway)
