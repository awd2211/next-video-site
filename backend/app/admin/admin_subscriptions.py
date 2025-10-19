"""
管理端 - 用户订阅管理 API

管理员可以查看所有订阅、手动取消订阅、查看订阅统计
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_

from app.database import get_db
from app.models.user import AdminUser
from app.models.subscription import UserSubscription, SubscriptionStatus
from app.schemas.subscription import (
    UserSubscriptionResponse,
    SubscriptionListResponse,
    SubscriptionCancelRequest,
)
from app.services.subscription_service import SubscriptionService
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


@router.get("/", response_model=SubscriptionListResponse)
async def list_all_subscriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[SubscriptionStatus] = Query(
        None, description="Filter by status"
    ),
    plan_id: Optional[int] = Query(None, description="Filter by plan ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取所有用户订阅

    管理员可以查看所有用户的订阅记录，支持多种筛选条件
    """
    query = select(UserSubscription)

    # 应用筛选条件
    conditions = []
    if status_filter:
        conditions.append(UserSubscription.status == status_filter)
    if plan_id:
        conditions.append(UserSubscription.plan_id == plan_id)
    if user_id:
        conditions.append(UserSubscription.user_id == user_id)
    if start_date:
        conditions.append(UserSubscription.created_at >= start_date)
    if end_date:
        conditions.append(UserSubscription.created_at <= end_date)

    if conditions:
        query = query.where(and_(*conditions))

    # 查询总数
    count_result = await db.execute(query)
    total = len(list(count_result.scalars().all()))

    # 查询列表
    result = await db.execute(
        query.order_by(desc(UserSubscription.created_at)).offset(skip).limit(limit)
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
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定订阅详情"""
    result = await db.execute(
        select(UserSubscription).where(UserSubscription.id == subscription_id)
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )

    return subscription


@router.post("/{subscription_id}/cancel", response_model=UserSubscriptionResponse)
async def admin_cancel_subscription(
    subscription_id: int,
    cancel_request: SubscriptionCancelRequest,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    管理员取消订阅

    管理员可以取消任何用户的订阅
    """
    service = SubscriptionService(db)

    # 获取订阅
    result = await db.execute(
        select(UserSubscription).where(UserSubscription.id == subscription_id)
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )

    try:
        subscription = await service.cancel_subscription(
            user_id=subscription.user_id,
            subscription_id=subscription_id,
            immediately=cancel_request.immediately,
            provider=None,  # 管理员操作可能不需要同步到支付网关
            gateway_config=None,
        )
        return subscription
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{subscription_id}/renew", response_model=UserSubscriptionResponse)
async def admin_renew_subscription(
    subscription_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    管理员手动续费订阅

    可用于处理支付失败后的手动续费
    """
    service = SubscriptionService(db)

    try:
        subscription = await service.renew_subscription(
            subscription_id=subscription_id,
            gateway_config=None,  # 手动续费不通过支付网关
        )
        return subscription
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/stats/overview", response_model=dict)
async def get_subscription_statistics(
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取订阅系统总览

    返回总订阅数、活跃订阅数、各状态订阅数等
    """
    # 查询所有订阅
    all_subs_result = await db.execute(select(UserSubscription))
    all_subs = list(all_subs_result.scalars().all())

    # 统计各状态数量
    active_count = len([s for s in all_subs if s.status == SubscriptionStatus.ACTIVE])
    trialing_count = len(
        [s for s in all_subs if s.status == SubscriptionStatus.TRIALING]
    )
    past_due_count = len(
        [s for s in all_subs if s.status == SubscriptionStatus.PAST_DUE]
    )
    canceled_count = len(
        [s for s in all_subs if s.status == SubscriptionStatus.CANCELED]
    )
    expired_count = len([s for s in all_subs if s.status == SubscriptionStatus.EXPIRED])

    # 计算月度经常性收入 (MRR)
    from decimal import Decimal

    active_subscriptions = [s for s in all_subs if s.status == SubscriptionStatus.ACTIVE]
    mrr = Decimal(0)
    for sub in active_subscriptions:
        if sub.plan:
            # 根据计费周期归一化为月度收入
            from app.models.subscription import BillingPeriod

            price = sub.plan.price_usd
            if sub.plan.billing_period == BillingPeriod.MONTHLY:
                mrr += price
            elif sub.plan.billing_period == BillingPeriod.QUARTERLY:
                mrr += price / 3
            elif sub.plan.billing_period == BillingPeriod.YEARLY:
                mrr += price / 12
            # LIFETIME 不计入 MRR

    # 计算流失率（简化版：本月取消的订阅数 / 上月活跃订阅数）
    now = datetime.now()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    canceled_this_month = [
        s
        for s in all_subs
        if s.canceled_at and s.canceled_at >= this_month_start
    ]
    churn_rate = (
        len(canceled_this_month) / active_count * 100 if active_count > 0 else 0
    )

    return {
        "total_subscriptions": len(all_subs),
        "active_subscriptions": active_count,
        "trialing_subscriptions": trialing_count,
        "past_due_subscriptions": past_due_count,
        "canceled_subscriptions": canceled_count,
        "expired_subscriptions": expired_count,
        "monthly_recurring_revenue": float(mrr),
        "churn_rate": round(churn_rate, 2),
    }


@router.get("/user/{user_id}/subscriptions", response_model=SubscriptionListResponse)
async def get_user_subscriptions(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取指定用户的所有订阅

    管理员可以查看任何用户的订阅历史
    """
    query = select(UserSubscription).where(UserSubscription.user_id == user_id)

    # 查询总数
    count_result = await db.execute(query)
    total = len(list(count_result.scalars().all()))

    # 查询列表
    result = await db.execute(
        query.order_by(desc(UserSubscription.created_at)).offset(skip).limit(limit)
    )
    subscriptions = list(result.scalars().all())

    return SubscriptionListResponse(
        items=subscriptions,
        total=total,
        skip=skip,
        limit=limit,
    )
