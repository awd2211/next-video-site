"""
支付系统 API

用户端支付管理端点
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.payment import PaymentProvider
from app.schemas.payment import (
    PaymentIntentRequest,
    PaymentIntentResponse,
    PaymentConfirmRequest,
    PaymentResponse,
    PaymentListResponse,
    RefundRequest,
    RefundResponse,
    PaymentMethodCreate,
    PaymentMethodUpdate,
    PaymentMethodResponse,
    PaymentMethodListResponse,
)
from app.services.payment_service import PaymentService
from app.services.payment_gateway import PaymentGatewayConfig
from app.utils.dependencies import get_current_user
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


@router.post("/intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    request: PaymentIntentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    创建支付意图

    流程：
    1. 在支付网关创建 PaymentIntent 或 Order
    2. 返回 client_secret 或 payment_url
    3. 前端使用返回的信息完成支付
    """
    service = PaymentService(db)
    gateway_config = get_gateway_config(request.provider)

    try:
        result = await service.create_payment_intent(
            user_id=current_user.id,
            request=request,
            gateway_config=gateway_config,
        )

        return PaymentIntentResponse(
            success=True,
            payment_id=result.get("payment_id"),
            provider_payment_id=result.get("provider_payment_id"),
            client_secret=result.get("client_secret"),
            payment_url=result.get("payment_url"),
            status=result.get("status"),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment intent: {str(e)}",
        )


@router.post("/confirm", response_model=PaymentResponse)
async def confirm_payment(
    request: PaymentConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    确认支付

    用于确认客户端完成的支付（Stripe、PayPal 回调后）
    """
    service = PaymentService(db)

    # 获取支付记录以确定提供商
    payment = await service.get_payment(current_user.id, request.payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    gateway_config = get_gateway_config(payment.provider)

    try:
        payment = await service.confirm_payment(
            user_id=current_user.id,
            request=request,
            gateway_config=gateway_config,
        )
        return payment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=PaymentListResponse)
async def list_my_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的支付记录"""
    service = PaymentService(db)
    payments, total = await service.list_user_payments(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )

    return PaymentListResponse(
        items=payments,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定支付记录详情"""
    service = PaymentService(db)
    payment = await service.get_payment(current_user.id, payment_id)

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return payment


@router.post("/{payment_id}/refund", response_model=RefundResponse)
async def request_refund(
    payment_id: int,
    request: RefundRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    申请退款

    注意：需要根据业务规则决定用户是否可以直接申请退款
    或者仅允许管理员处理退款
    """
    service = PaymentService(db)

    # 验证 payment_id 匹配
    if request.payment_id != payment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment ID mismatch",
        )

    # 获取支付记录以确定提供商
    payment = await service.get_payment(current_user.id, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    gateway_config = get_gateway_config(payment.provider)

    try:
        result = await service.create_refund(
            user_id=current_user.id,
            request=request,
            gateway_config=gateway_config,
        )

        return RefundResponse(
            success=result.get("success", False),
            refund_id=result.get("refund_id"),
            amount=result.get("amount"),
            total_refunded=result.get("total_refunded"),
            payment_status=result.get("payment_status"),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ==================== 支付方式管理 ====================


@router.get("/methods/", response_model=PaymentMethodListResponse)
async def list_payment_methods(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取用户保存的支付方式列表"""
    service = PaymentService(db)
    methods = await service.list_payment_methods(current_user.id)

    return PaymentMethodListResponse(
        items=methods,
        total=len(methods),
    )


@router.post("/methods/", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED)
async def add_payment_method(
    method_data: PaymentMethodCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    添加支付方式

    注意：
    - provider_payment_method_id 应该是支付网关返回的 token/ID
    - 不应该在此接口传输敏感卡号信息
    - 前端应该使用支付网关的 SDK 完成卡信息收集
    """
    service = PaymentService(db)

    try:
        method = await service.add_payment_method(
            user_id=current_user.id,
            provider=method_data.provider,
            provider_payment_method_id=method_data.provider_payment_method_id,
            card_info={
                "type": method_data.type,
                "brand": method_data.card_brand,
                "last4": method_data.card_last4,
                "exp_month": method_data.card_exp_month,
                "exp_year": method_data.card_exp_year,
            },
            is_default=method_data.is_default,
        )
        return method
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/methods/{method_id}", response_model=PaymentMethodResponse)
async def get_payment_method(
    method_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定支付方式详情"""
    service = PaymentService(db)
    method = await service.get_payment_method(current_user.id, method_id)

    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found",
        )

    return method


@router.patch("/methods/{method_id}/default", response_model=PaymentMethodResponse)
async def set_default_payment_method(
    method_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """设置默认支付方式"""
    service = PaymentService(db)

    try:
        method = await service.set_default_payment_method(current_user.id, method_id)
        return method
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/methods/{method_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment_method(
    method_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除支付方式（软删除）"""
    service = PaymentService(db)

    try:
        await service.delete_payment_method(current_user.id, method_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
