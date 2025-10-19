"""
Alipay (支付宝) 支付网关实现

支持支付宝账户支付
"""

import hashlib
import base64
from decimal import Decimal
from typing import Optional, Dict, Any
from datetime import datetime
from urllib.parse import urlencode, quote_plus
import httpx

from app.services.payment_gateway import (
    PaymentGateway,
    PaymentGatewayConfig,
    PaymentResult,
    RefundResult,
    PaymentGatewayException,
    PaymentGatewayFactory,
)
from app.models.payment import PaymentProvider, Currency


class AlipayGateway(PaymentGateway):
    """Alipay 支付网关"""

    def __init__(self, config: PaymentGatewayConfig):
        super().__init__(config)
        self.app_id = config.api_key
        self.private_key = config.api_secret
        self.alipay_public_key = config.extra_config.get("alipay_public_key")

        # API 基础 URL
        if config.environment == "production":
            self.gateway_url = "https://openapi.alipay.com/gateway.do"
        else:
            self.gateway_url = "https://openapi.alipaydev.com/gateway.do"

    def _sign(self, params: Dict[str, Any]) -> str:
        """
        生成签名

        注意: 实际生产环境中应使用 RSA2 签名
        这里简化实现
        """
        # 排序参数
        sorted_params = sorted(params.items())
        unsigned_string = "&".join(f"{k}={v}" for k, v in sorted_params if v)

        # 使用 RSA 私钥签名 (简化版本，实际应使用 Crypto 库)
        # sign = rsa.sign(unsigned_string.encode('utf-8'), private_key, 'SHA-256')
        # return base64.b64encode(sign).decode('utf-8')

        # 临时使用 MD5 签名 (仅用于演示)
        sign_str = unsigned_string + self.private_key
        return hashlib.md5(sign_str.encode("utf-8")).hexdigest()

    def _verify_signature(self, params: Dict[str, Any], signature: str) -> bool:
        """验证签名"""
        # 实际生产环境中应使用 RSA 公钥验证
        # 这里简化实现
        return True

    async def _make_request(self, method: str, biz_content: Dict[str, Any]) -> Dict[str, Any]:
        """发起支付宝 API 请求"""
        params = {
            "app_id": self.app_id,
            "method": method,
            "format": "JSON",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": str(biz_content),
        }

        # 生成签名
        params["sign"] = self._sign(params)

        async with httpx.AsyncClient() as client:
            response = await client.post(self.gateway_url, data=params)

            if response.status_code != 200:
                raise PaymentGatewayException(f"Alipay API error: {response.text}")

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
        """创建支付宝订单"""
        try:
            # 生成订单号
            out_trade_no = f"PAY{datetime.now().strftime('%Y%m%d%H%M%S')}{metadata.get('user_id', '000')}"

            biz_content = {
                "out_trade_no": out_trade_no,
                "total_amount": str(amount),
                "subject": description or "Payment",
                "product_code": "QUICK_WAP_WAY",  # 手机网站支付
            }

            if metadata:
                biz_content["passback_params"] = urlencode(metadata)

            # 构建支付宝支付表单
            response = await self._make_request("alipay.trade.wap.pay", biz_content)

            # 构建支付 URL
            payment_url = f"{self.gateway_url}?{urlencode(response)}"

            return PaymentResult(
                success=True,
                provider_payment_id=out_trade_no,
                status="WAIT_BUYER_PAY",
                metadata={
                    "payment_url": payment_url,
                    "out_trade_no": out_trade_no,
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
        """
        确认支付宝支付

        注意: 支付宝的支付通过用户在支付宝页面完成
        这里查询支付状态
        """
        return await self.get_payment_status(payment_intent_id)

    async def get_payment_status(self, payment_id: str) -> PaymentResult:
        """查询支付宝订单状态"""
        try:
            biz_content = {
                "out_trade_no": payment_id,
            }

            response = await self._make_request("alipay.trade.query", biz_content)

            # 解析响应
            response_key = "alipay_trade_query_response"
            if response_key not in response:
                raise PaymentGatewayException("Invalid Alipay response")

            result = response[response_key]

            if result["code"] != "10000":
                raise PaymentGatewayException(f"Alipay error: {result.get('sub_msg', result.get('msg'))}")

            return PaymentResult(
                success=result["trade_status"] == "TRADE_SUCCESS",
                provider_payment_id=result["trade_no"],
                amount=Decimal(result["total_amount"]),
                currency=Currency.CNY,  # 支付宝主要使用人民币
                status=result["trade_status"],
            )

        except Exception as e:
            raise PaymentGatewayException(f"Failed to get payment status: {e}")

    async def create_refund(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None,
    ) -> RefundResult:
        """创建支付宝退款"""
        try:
            # 生成退款单号
            out_request_no = f"REF{datetime.now().strftime('%Y%m%d%H%M%S')}"

            biz_content = {
                "out_trade_no": payment_id,
                "refund_amount": str(amount) if amount else None,
                "refund_reason": reason or "用户申请退款",
                "out_request_no": out_request_no,
            }

            response = await self._make_request("alipay.trade.refund", biz_content)

            response_key = "alipay_trade_refund_response"
            if response_key not in response:
                raise PaymentGatewayException("Invalid Alipay refund response")

            result = response[response_key]

            return RefundResult(
                success=result["code"] == "10000" and result.get("fund_change") == "Y",
                refund_id=result.get("trade_no"),
                amount=Decimal(result["refund_fee"]) if result.get("refund_fee") else None,
                refunded_at=datetime.now(),
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
        创建支付宝客户

        注意: 支付宝使用 user_id (买家支付宝用户号)
        这里返回 email 作为临时标识
        """
        return email

    async def attach_payment_method(
        self,
        customer_id: str,
        payment_method_id: str,
    ) -> bool:
        """
        关联支付方式

        注意: 支付宝的支付方式在用户端管理
        """
        return True

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        创建支付宝周期扣款 (代扣)

        注意: 支付宝的周期扣款需要用户签约
        """
        try:
            # 生成协议号
            external_agreement_no = f"SUB{datetime.now().strftime('%Y%m%d%H%M%S')}"

            biz_content = {
                "external_agreement_no": external_agreement_no,
                "personal_product_code": "CYCLE_PAY_AUTH_P",
                "sign_scene": "INDUSTRY|DIGITAL_MEDIA",
                "product_code": price_id,
            }

            response = await self._make_request("alipay.user.agreement.page.sign", biz_content)

            return {
                "subscription_id": external_agreement_no,
                "status": "TEMP",
                "sign_url": response.get("sign_str"),
                "current_period_start": None,
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
        """取消支付宝周期扣款"""
        try:
            biz_content = {
                "agreement_no": subscription_id,
                "terminate_reason": "用户主动解约",
            }

            response = await self._make_request("alipay.user.agreement.unsign", biz_content)

            response_key = "alipay_user_agreement_unsign_response"
            result = response.get(response_key, {})

            return result.get("code") == "10000"

        except Exception as e:
            raise PaymentGatewayException(f"Failed to cancel subscription: {e}")

    async def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
    ) -> bool:
        """验证支付宝回调签名"""
        try:
            # 解析参数
            params = {}
            for item in payload.decode("utf-8").split("&"):
                if "=" in item:
                    k, v = item.split("=", 1)
                    params[k] = v

            # 验证签名
            return self._verify_signature(params, signature)

        except Exception:
            return False


# 注册到工厂
PaymentGatewayFactory.register(PaymentProvider.ALIPAY, AlipayGateway)
