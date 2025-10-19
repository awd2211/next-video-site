"""
订阅系统 API

用户端订阅管理端点
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.payment import PaymentProvider
from app.schemas.subscription import (
    SubscriptionPlanResponse,
    SubscriptionPlanListResponse,
    UserSubscriptionCreate,
    UserSubscriptionUpdate,
    UserSubscriptionResponse,
    SubscriptionCancelRequest,
    SubscriptionListResponse,
)
from app.services.subscription_service import SubscriptionService
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


@router.get("/plans", response_model=SubscriptionPlanListResponse)
async def list_subscription_plans(
    skip: int = Query(0, ge=0, description="Skip records"),
    limit: int = Query(20, ge=1, le=100, description="Limit records"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取所有可用的订阅套餐

    返回激活状态的订阅套餐列表，按显示顺序排序
    """
    service = SubscriptionService(db)
    plans = await service.list_active_plans()

    # 简单分页
    total = len(plans)
    plans_page = plans[skip : skip + limit]

    return SubscriptionPlanListResponse(
        items=plans_page,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/plans/{plan_id}", response_model=SubscriptionPlanResponse)
async def get_subscription_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取指定订阅套餐详情"""
    service = SubscriptionService(db)
    plan = await service.get_plan(plan_id)

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found",
        )

    if not plan.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subscription plan is not available",
        )

    return plan


@router.post("/", response_model=UserSubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: UserSubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    创建新订阅

    流程：
    1. 验证套餐和优惠券
    2. 在支付网关创建订阅
    3. 创建本地订阅记录
    4. 返回订阅详情
    """
    service = SubscriptionService(db)

    # 获取支付网关配置 (默认使用 Stripe)
    provider = PaymentProvider.STRIPE
    gateway_config = get_gateway_config(provider)

    try:
        subscription = await service.create_subscription(
            user_id=current_user.id,
            subscription_data=subscription_data,
            provider=provider,
            gateway_config=gateway_config,
        )
        return subscription
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}",
        )


@router.get("/me", response_model=Optional[UserSubscriptionResponse])
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的激活订阅"""
    service = SubscriptionService(db)
    subscription = await service.get_active_subscription(current_user.id)

    return subscription


@router.get("/", response_model=SubscriptionListResponse)
async def list_my_subscriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的所有订阅记录（含历史）"""
    from sqlalchemy import select, desc
    from app.models.subscription import UserSubscription

    # 查询总数
    count_result = await db.execute(
        select(UserSubscription).where(UserSubscription.user_id == current_user.id)
    )
    total = len(list(count_result.scalars().all()))

    # 查询列表
    result = await db.execute(
        select(UserSubscription)
        .where(UserSubscription.user_id == current_user.id)
        .order_by(desc(UserSubscription.created_at))
        .offset(skip)
        .limit(limit)
    )
    subscriptions = list(result.scalars().all())

    return SubscriptionListResponse(
        items=subscriptions,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{subscription_id}", response_model=UserSubscriptionResponse)
async def get_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定订阅详情"""
    service = SubscriptionService(db)
    subscription = await service.get_user_subscription(current_user.id, subscription_id)

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )

    return subscription


@router.patch("/{subscription_id}", response_model=UserSubscriptionResponse)
async def update_subscription(
    subscription_id: int,
    update_data: UserSubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新订阅设置

    可更新：
    - auto_renew: 自动续费开关
    - payment_method_id: 支付方式
    """
    service = SubscriptionService(db)

    try:
        subscription = await service.update_subscription(
            user_id=current_user.id,
            subscription_id=subscription_id,
            update_data=update_data,
        )
        return subscription
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/{subscription_id}/cancel", response_model=UserSubscriptionResponse)
async def cancel_subscription(
    subscription_id: int,
    cancel_request: SubscriptionCancelRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    取消订阅

    支持两种模式：
    - immediately=false: 期末取消，继续使用到当前周期结束
    - immediately=true: 立即取消，马上停止服务
    """
    service = SubscriptionService(db)

    # 获取订阅以确定支付提供商
    subscription = await service.get_user_subscription(current_user.id, subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )

    # 确定使用的支付提供商
    provider = None
    if subscription.stripe_subscription_id:
        provider = PaymentProvider.STRIPE
    elif subscription.paypal_subscription_id:
        provider = PaymentProvider.PAYPAL

    gateway_config = get_gateway_config(provider) if provider else None

    try:
        subscription = await service.cancel_subscription(
            user_id=current_user.id,
            subscription_id=subscription_id,
            immediately=cancel_request.immediately,
            provider=provider,
            gateway_config=gateway_config,
        )
        return subscription
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
