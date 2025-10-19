"""
Webhook 处理端点

接收支付网关的异步通知
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.payment import PaymentProvider
from app.services.payment_service import PaymentService
from app.services.payment_gateway import PaymentGatewayConfig
from app.config import get_settings

router = APIRouter()
settings = get_settings()


def get_gateway_config(provider: PaymentProvider) -> PaymentGatewayConfig:
    """获取支付网关配置"""
    if provider == PaymentProvider.STRIPE:
        return PaymentGatewayConfig(
            provider=PaymentProvider.STRIPE,
            api_key=settings.STRIPE_SECRET_KEY,
            webhook_secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    elif provider == PaymentProvider.PAYPAL:
        return PaymentGatewayConfig(
            provider=PaymentProvider.PAYPAL,
            api_key=settings.PAYPAL_CLIENT_ID,
            api_secret=settings.PAYPAL_CLIENT_SECRET,
            environment=settings.PAYPAL_ENVIRONMENT,
        )
    elif provider == PaymentProvider.ALIPAY:
        return PaymentGatewayConfig(
            provider=PaymentProvider.ALIPAY,
            api_key=settings.ALIPAY_APP_ID,
            api_secret=settings.ALIPAY_PRIVATE_KEY,
            public_key=settings.ALIPAY_PUBLIC_KEY,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported payment provider: {provider}",
        )


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    db: AsyncSession = Depends(get_db),
):
    """
    Stripe Webhook 处理

    接收 Stripe 的事件通知，如：
    - payment_intent.succeeded
    - payment_intent.payment_failed
    - customer.subscription.created
    - customer.subscription.deleted
    """
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe-Signature header",
        )

    payload = await request.body()
    gateway_config = get_gateway_config(PaymentProvider.STRIPE)

    service = PaymentService(db)

    try:
        result = await service.handle_webhook(
            provider=PaymentProvider.STRIPE,
            payload=payload,
            signature=stripe_signature,
            gateway_config=gateway_config,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}",
        )


@router.post("/paypal")
async def paypal_webhook(
    request: Request,
    paypal_transmission_id: str = Header(None, alias="PAYPAL-TRANSMISSION-ID"),
    paypal_transmission_time: str = Header(None, alias="PAYPAL-TRANSMISSION-TIME"),
    paypal_transmission_sig: str = Header(None, alias="PAYPAL-TRANSMISSION-SIG"),
    paypal_cert_url: str = Header(None, alias="PAYPAL-CERT-URL"),
    db: AsyncSession = Depends(get_db),
):
    """
    PayPal Webhook 处理

    接收 PayPal 的事件通知，如：
    - PAYMENT.CAPTURE.COMPLETED
    - PAYMENT.CAPTURE.DENIED
    - BILLING.SUBSCRIPTION.CREATED
    - BILLING.SUBSCRIPTION.CANCELLED
    """
    # PayPal 使用多个 header 进行签名验证
    signature_headers = {
        "transmission_id": paypal_transmission_id,
        "transmission_time": paypal_transmission_time,
        "transmission_sig": paypal_transmission_sig,
        "cert_url": paypal_cert_url,
    }

    # 简化处理，实际应该验证所有 header
    if not paypal_transmission_sig:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing PayPal signature headers",
        )

    payload = await request.body()
    gateway_config = get_gateway_config(PaymentProvider.PAYPAL)

    service = PaymentService(db)

    try:
        result = await service.handle_webhook(
            provider=PaymentProvider.PAYPAL,
            payload=payload,
            signature=paypal_transmission_sig,
            gateway_config=gateway_config,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}",
        )


@router.post("/alipay")
async def alipay_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Alipay Webhook 处理

    接收支付宝的异步通知，如：
    - trade_status_sync (交易状态同步)
    - refund_fastpay_by_platform_nopwd (退款通知)
    """
    # 支付宝使用 form data 传输
    form_data = await request.form()
    sign = form_data.get("sign", "")

    if not sign:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Alipay signature",
        )

    payload = await request.body()
    gateway_config = get_gateway_config(PaymentProvider.ALIPAY)

    service = PaymentService(db)

    try:
        result = await service.handle_webhook(
            provider=PaymentProvider.ALIPAY,
            payload=payload,
            signature=sign,
            gateway_config=gateway_config,
        )

        # 支付宝要求返回 "success" 字符串
        return {"success": True, "result": "success"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        # 即使处理失败，也应该返回 success 避免支付宝重试
        # 但应该记录错误日志
        print(f"Alipay webhook error: {e}")
        return {"success": False, "result": "fail"}
