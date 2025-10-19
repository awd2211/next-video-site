"""
管理端 - 优惠券管理 API

管理员可以创建、编辑、删除优惠券，查看使用统计
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import AdminUser
from app.models.coupon import CouponStatus
from app.schemas.coupon import (
    CouponCreate,
    CouponUpdate,
    CouponResponse,
    CouponListResponse,
)
from app.services.coupon_service import CouponService
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


@router.get("/", response_model=CouponListResponse)
async def list_all_coupons(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[CouponStatus] = Query(None, description="Filter by status"),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取所有优惠券

    管理员可以查看所有优惠券，包括已停用的
    """
    service = CouponService(db)
    coupons, total = await service.list_coupons(
        status=status_filter,
        skip=skip,
        limit=limit,
    )

    return CouponListResponse(
        items=coupons,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{coupon_id}", response_model=CouponResponse)
async def get_coupon(
    coupon_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定优惠券详情"""
    service = CouponService(db)
    coupon = await service.get_coupon(coupon_id)

    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found",
        )

    return coupon


@router.post("/", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
async def create_coupon(
    coupon_data: CouponCreate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    创建新优惠券

    只有管理员可以创建优惠券
    """
    service = CouponService(db)

    try:
        coupon = await service.create_coupon(
            coupon_data=coupon_data,
            admin_id=current_admin.id,
        )
        return coupon
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch("/{coupon_id}", response_model=CouponResponse)
async def update_coupon(
    coupon_id: int,
    update_data: CouponUpdate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新优惠券

    可以更新优惠券的所有字段
    """
    service = CouponService(db)

    try:
        coupon = await service.update_coupon(
            coupon_id=coupon_id,
            update_data=update_data,
        )
        return coupon
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/{coupon_id}/activate", response_model=CouponResponse)
async def activate_coupon(
    coupon_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """激活优惠券"""
    service = CouponService(db)

    try:
        coupon = await service.activate_coupon(coupon_id)
        return coupon
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/{coupon_id}/deactivate", response_model=CouponResponse)
async def deactivate_coupon(
    coupon_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """停用优惠券"""
    service = CouponService(db)

    try:
        coupon = await service.deactivate_coupon(coupon_id)
        return coupon
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{coupon_id}/statistics", response_model=dict)
async def get_coupon_statistics(
    coupon_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取优惠券使用统计

    返回总使用次数、独立用户数、总折扣金额等
    """
    service = CouponService(db)

    try:
        stats = await service.get_coupon_statistics(coupon_id)
        return stats
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/code/{code}", response_model=CouponResponse)
async def get_coupon_by_code(
    code: str,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """根据优惠券代码查询"""
    service = CouponService(db)
    coupon = await service.get_coupon_by_code(code)

    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found",
        )

    return coupon


@router.get("/stats/overview", response_model=dict)
async def get_coupon_overview(
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取优惠券系统总览

    返回总优惠券数、活跃优惠券数、总使用次数等
    """
    from app.models.coupon import Coupon
    from sqlalchemy import select, func

    service = CouponService(db)

    # 查询所有优惠券
    all_coupons_result = await db.execute(select(Coupon))
    all_coupons = list(all_coupons_result.scalars().all())

    # 统计各状态数量
    active_count = len([c for c in all_coupons if c.status == CouponStatus.ACTIVE])
    disabled_count = len([c for c in all_coupons if c.status == CouponStatus.DISABLED])
    expired_count = len([c for c in all_coupons if c.status == CouponStatus.EXPIRED])

    # 统计总使用次数
    total_usage = sum(c.usage_count for c in all_coupons)

    # 统计总折扣金额（需要查询订阅记录）
    from app.models.subscription import UserSubscription
    from decimal import Decimal

    subs_result = await db.execute(
        select(UserSubscription).where(UserSubscription.coupon_id.isnot(None))
    )
    subscriptions = list(subs_result.scalars().all())
    total_discount = sum(sub.discount_amount for sub in subscriptions)

    # 找出最常用的优惠券
    most_used = max(all_coupons, key=lambda c: c.usage_count) if all_coupons else None

    return {
        "total_coupons": len(all_coupons),
        "active_coupons": active_count,
        "disabled_coupons": disabled_count,
        "expired_coupons": expired_count,
        "total_usage": total_usage,
        "total_discount_amount": float(total_discount),
        "most_used_coupon": {
            "code": most_used.code,
            "usage_count": most_used.usage_count,
        }
        if most_used
        else None,
    }
