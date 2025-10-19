"""
优惠券系统 API

用户端优惠券验证和查询端点
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.coupon import (
    CouponResponse,
    CouponValidateRequest,
    CouponValidateResponse,
)
from app.services.coupon_service import CouponService
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.post("/validate", response_model=CouponValidateResponse)
async def validate_coupon(
    request: CouponValidateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    验证优惠券

    检查优惠券是否可用，并计算折扣金额

    业务规则：
    - 检查优惠券是否存在
    - 检查时间有效性
    - 检查最低消费金额
    - 检查适用套餐
    - 检查是否仅限首次购买
    - 检查每用户使用次数限制
    """
    service = CouponService(db)

    result = await service.validate_coupon(
        code=request.code,
        user_id=current_user.id,
        plan_id=request.plan_id,
        amount=request.amount,
    )

    return CouponValidateResponse(
        valid=result["valid"],
        coupon=result.get("coupon"),
        discount_amount=result.get("discount_amount", 0),
        final_amount=result.get("final_amount", request.amount),
        error_message=result.get("error_message"),
    )


@router.get("/available", response_model=List[CouponResponse])
async def list_available_coupons(
    plan_id: Optional[int] = Query(None, description="Filter by applicable plan"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取用户可用的优惠券列表

    返回当前用户可以使用的所有优惠券
    可选按套餐ID筛选
    """
    service = CouponService(db)
    coupons = await service.get_user_available_coupons(
        user_id=current_user.id,
        plan_id=plan_id,
    )

    return coupons


@router.get("/{code}", response_model=CouponResponse)
async def get_coupon_by_code(
    code: str,
    db: AsyncSession = Depends(get_db),
):
    """
    根据代码获取优惠券信息

    公开接口，任何人都可以查看优惠券详情
    """
    service = CouponService(db)
    coupon = await service.get_coupon_by_code(code)

    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found",
        )

    return coupon
