"""
优惠券系统 Pydantic Schemas
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from app.models.coupon import DiscountType, CouponStatus


class CouponBase(BaseModel):
    """优惠券基础 Schema"""
    code: str = Field(..., min_length=1, max_length=50, description="优惠券代码")
    discount_type: DiscountType = Field(..., description="折扣类型")
    discount_value: Decimal = Field(..., gt=0, description="折扣值")
    max_discount_amount: Optional[Decimal] = Field(None, gt=0, description="最大折扣金额")

    usage_limit: Optional[int] = Field(None, gt=0, description="总使用次数限制")
    usage_limit_per_user: int = Field(default=1, gt=0, description="每个用户使用次数限制")

    minimum_amount: Optional[Decimal] = Field(None, gt=0, description="最低消费金额")
    applicable_plans: Optional[str] = Field(None, description="适用套餐ID列表 JSON")

    valid_from: datetime = Field(..., description="有效期开始")
    valid_until: Optional[datetime] = Field(None, description="有效期结束")

    is_first_purchase_only: bool = Field(default=False, description="是否仅限首次购买")
    description: Optional[str] = Field(None, description="描述")

    @field_validator("valid_until")
    @classmethod
    def validate_valid_until(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """验证有效期结束时间"""
        if v and "valid_from" in info.data:
            if v <= info.data["valid_from"]:
                raise ValueError("valid_until must be after valid_from")
        return v


class CouponCreate(CouponBase):
    """创建优惠券 (管理员)"""
    status: CouponStatus = Field(default=CouponStatus.ACTIVE, description="状态")


class CouponUpdate(BaseModel):
    """更新优惠券 (管理员)"""
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    discount_type: Optional[DiscountType] = None
    discount_value: Optional[Decimal] = Field(None, gt=0)
    max_discount_amount: Optional[Decimal] = Field(None, gt=0)

    usage_limit: Optional[int] = Field(None, gt=0)
    usage_limit_per_user: Optional[int] = Field(None, gt=0)

    minimum_amount: Optional[Decimal] = Field(None, gt=0)
    applicable_plans: Optional[str] = None

    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None

    status: Optional[CouponStatus] = None
    is_first_purchase_only: Optional[bool] = None
    description: Optional[str] = None


class CouponResponse(BaseModel):
    """优惠券响应"""
    id: int
    code: str
    discount_type: DiscountType
    discount_value: Decimal
    max_discount_amount: Optional[Decimal] = None

    usage_limit: Optional[int] = None
    usage_count: int
    usage_limit_per_user: int

    minimum_amount: Optional[Decimal] = None
    applicable_plans: Optional[str] = None

    valid_from: datetime
    valid_until: Optional[datetime] = None

    status: CouponStatus
    is_first_purchase_only: bool

    description: Optional[str] = None
    created_by: Optional[int] = None

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CouponValidateRequest(BaseModel):
    """验证优惠券请求"""
    code: str = Field(..., min_length=1, max_length=50, description="优惠券代码")
    plan_id: int = Field(..., description="套餐ID")
    amount: Decimal = Field(..., gt=0, description="订单金额")


class CouponValidateResponse(BaseModel):
    """验证优惠券响应"""
    valid: bool
    coupon: Optional[CouponResponse] = None
    discount_amount: Decimal = Field(default=0, description="折扣金额")
    final_amount: Decimal = Field(..., description="最终金额")
    error_message: Optional[str] = None


class CouponListResponse(BaseModel):
    """优惠券列表响应"""
    items: List[CouponResponse]
    total: int
    skip: int
    limit: int
