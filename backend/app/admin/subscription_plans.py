"""
管理端 - 订阅套餐管理 API

管理员可以创建、编辑、删除订阅套餐
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models.user import AdminUser
from app.models.subscription import SubscriptionPlan
from app.schemas.subscription import (
    SubscriptionPlanCreate,
    SubscriptionPlanUpdate,
    SubscriptionPlanResponse,
    SubscriptionPlanListResponse,
)
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


@router.get("/", response_model=SubscriptionPlanListResponse)
async def list_subscription_plans(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取所有订阅套餐（包括已停用）

    管理员可以查看所有套餐，包括未激活的
    """
    # 转换为 skip/limit
    skip = (page - 1) * page_size
    limit = page_size

    query = select(SubscriptionPlan)

    if is_active is not None:
        query = query.where(SubscriptionPlan.is_active == is_active)

    # 查询总数
    count_result = await db.execute(query)
    total = len(list(count_result.scalars().all()))

    # 查询列表
    result = await db.execute(
        query.order_by(SubscriptionPlan.display_order, SubscriptionPlan.id)
        .offset(skip)
        .limit(limit)
    )
    plans = list(result.scalars().all())

    return SubscriptionPlanListResponse(
        items=plans,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{plan_id}", response_model=SubscriptionPlanResponse)
async def get_subscription_plan(
    plan_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定订阅套餐详情"""
    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found",
        )

    return plan


@router.post("/", response_model=SubscriptionPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription_plan(
    plan_data: SubscriptionPlanCreate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    创建新的订阅套餐

    只有管理员可以创建套餐
    """
    plan = SubscriptionPlan(
        name=plan_data.name,
        name_en=plan_data.name_en,
        name_zh=plan_data.name_zh,
        description=plan_data.description,
        description_en=plan_data.description_en,
        description_zh=plan_data.description_zh,
        billing_period=plan_data.billing_period,
        price_usd=plan_data.price_usd,
        price_cny=plan_data.price_cny,
        price_eur=plan_data.price_eur,
        trial_days=plan_data.trial_days,
        features=plan_data.features,
        max_video_quality=plan_data.max_video_quality,
        max_concurrent_streams=plan_data.max_concurrent_streams,
        allow_downloads=plan_data.allow_downloads,
        ad_free=plan_data.ad_free,
        is_active=plan_data.is_active,
        is_popular=plan_data.is_popular,
        display_order=plan_data.display_order,
    )

    db.add(plan)
    await db.commit()
    await db.refresh(plan)

    return plan


@router.put("/{plan_id}", response_model=SubscriptionPlanResponse)
@router.patch("/{plan_id}", response_model=SubscriptionPlanResponse)
async def update_subscription_plan(
    plan_id: int,
    update_data: SubscriptionPlanUpdate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新订阅套餐

    可以更新套餐的所有字段
    """
    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found",
        )

    # 更新字段
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(plan, field, value)

    await db.commit()
    await db.refresh(plan)

    return plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription_plan(
    plan_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除订阅套餐

    注意：如果有用户正在使用该套餐，应该先停用而不是删除
    建议使用软删除（设置 is_active = False）
    """
    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found",
        )

    # 检查是否有活跃订阅
    from app.models.subscription import UserSubscription, SubscriptionStatus

    active_subs_result = await db.execute(
        select(UserSubscription).where(
            UserSubscription.plan_id == plan_id,
            UserSubscription.status.in_(
                [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]
            ),
        )
    )
    active_subs = list(active_subs_result.scalars().all())

    if active_subs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete plan with {len(active_subs)} active subscriptions. Please deactivate it instead.",
        )

    await db.delete(plan)
    await db.commit()


@router.post("/{plan_id}/activate", response_model=SubscriptionPlanResponse)
async def activate_plan(
    plan_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """激活订阅套餐"""
    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found",
        )

    plan.is_active = True
    await db.commit()
    await db.refresh(plan)

    return plan


@router.post("/{plan_id}/deactivate", response_model=SubscriptionPlanResponse)
async def deactivate_plan(
    plan_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """停用订阅套餐（软删除）"""
    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found",
        )

    plan.is_active = False
    await db.commit()
    await db.refresh(plan)

    return plan


@router.get("/{plan_id}/subscriptions", response_model=dict)
async def get_plan_subscriptions(
    plan_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取使用该套餐的订阅统计

    返回活跃订阅数、总订阅数等信息
    """
    from app.models.subscription import UserSubscription, SubscriptionStatus

    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found",
        )

    # 查询所有订阅
    all_subs_result = await db.execute(
        select(UserSubscription).where(UserSubscription.plan_id == plan_id)
    )
    all_subs = list(all_subs_result.scalars().all())

    # 统计各状态订阅数
    active_count = len(
        [s for s in all_subs if s.status == SubscriptionStatus.ACTIVE]
    )
    trialing_count = len(
        [s for s in all_subs if s.status == SubscriptionStatus.TRIALING]
    )
    canceled_count = len(
        [s for s in all_subs if s.status == SubscriptionStatus.CANCELED]
    )
    expired_count = len(
        [s for s in all_subs if s.status == SubscriptionStatus.EXPIRED]
    )

    return {
        "plan_id": plan_id,
        "plan_name": plan.name,
        "total_subscriptions": len(all_subs),
        "active_subscriptions": active_count,
        "trialing_subscriptions": trialing_count,
        "canceled_subscriptions": canceled_count,
        "expired_subscriptions": expired_count,
    }
