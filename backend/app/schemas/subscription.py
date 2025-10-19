"""
订阅系统 Pydantic Schemas
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from app.models.subscription import BillingPeriod, SubscriptionStatus


# ==================== SubscriptionPlan Schemas ====================

class SubscriptionPlanBase(BaseModel):
    """订阅套餐基础 Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="套餐名称")
    name_en: Optional[str] = Field(None, max_length=100, description="英文名称")
    name_zh: Optional[str] = Field(None, max_length=100, description="中文名称")
    description: Optional[str] = Field(None, description="套餐描述")
    description_en: Optional[str] = Field(None, description="英文描述")
    description_zh: Optional[str] = Field(None, description="中文描述")

    billing_period: BillingPeriod = Field(..., description="计费周期")
    price_usd: Decimal = Field(..., ge=0, description="美元价格")
    price_cny: Decimal = Field(..., ge=0, description="人民币价格")
    price_eur: Optional[Decimal] = Field(None, ge=0, description="欧元价格")

    trial_days: int = Field(default=0, ge=0, le=365, description="试用天数")

    # 权限和限制
    features: Optional[str] = Field(None, description="功能列表 JSON")
    max_video_quality: str = Field(default="1080p", description="最高视频质量")
    max_concurrent_streams: int = Field(default=1, ge=1, le=10, description="最大并发播放数")
    allow_downloads: bool = Field(default=False, description="是否允许下载")
    ad_free: bool = Field(default=False, description="是否无广告")

    is_active: bool = Field(default=True, description="是否启用")
    is_popular: bool = Field(default=False, description="是否热门推荐")
    display_order: int = Field(default=0, description="显示顺序")


class SubscriptionPlanCreate(SubscriptionPlanBase):
    """创建订阅套餐"""
    pass


class SubscriptionPlanUpdate(BaseModel):
    """更新订阅套餐"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    name_en: Optional[str] = Field(None, max_length=100)
    name_zh: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    description_en: Optional[str] = None
    description_zh: Optional[str] = None

    billing_period: Optional[BillingPeriod] = None
    price_usd: Optional[Decimal] = Field(None, ge=0)
    price_cny: Optional[Decimal] = Field(None, ge=0)
    price_eur: Optional[Decimal] = Field(None, ge=0)

    trial_days: Optional[int] = Field(None, ge=0, le=365)

    features: Optional[str] = None
    max_video_quality: Optional[str] = None
    max_concurrent_streams: Optional[int] = Field(None, ge=1, le=10)
    allow_downloads: Optional[bool] = None
    ad_free: Optional[bool] = None

    is_active: Optional[bool] = None
    is_popular: Optional[bool] = None
    display_order: Optional[int] = None


class SubscriptionPlanResponse(SubscriptionPlanBase):
    """订阅套餐响应"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubscriptionPlanListResponse(BaseModel):
    """订阅套餐列表响应"""
    items: List[SubscriptionPlanResponse]
    total: int
    skip: int
    limit: int


# ==================== UserSubscription Schemas ====================

class UserSubscriptionBase(BaseModel):
    """用户订阅基础 Schema"""
    plan_id: int = Field(..., description="套餐ID")
    auto_renew: bool = Field(default=True, description="是否自动续费")


class UserSubscriptionCreate(UserSubscriptionBase):
    """创建用户订阅"""
    payment_method_id: Optional[int] = Field(None, description="默认支付方式")
    coupon_code: Optional[str] = Field(None, max_length=50, description="优惠券代码")


class UserSubscriptionUpdate(BaseModel):
    """更新用户订阅"""
    auto_renew: Optional[bool] = None
    payment_method_id: Optional[int] = None


class UserSubscriptionResponse(BaseModel):
    """用户订阅响应"""
    id: int
    user_id: int
    plan_id: int
    status: SubscriptionStatus

    start_date: datetime
    end_date: datetime
    trial_end_date: Optional[datetime] = None
    canceled_at: Optional[datetime] = None

    auto_renew: bool
    renew_at: Optional[datetime] = None

    discount_amount: Decimal

    created_at: datetime
    updated_at: Optional[datetime] = None

    # 关联对象
    plan: Optional[SubscriptionPlanResponse] = None

    class Config:
        from_attributes = True


class SubscriptionCancelRequest(BaseModel):
    """取消订阅请求"""
    immediately: bool = Field(default=False, description="是否立即取消")
    reason: Optional[str] = Field(None, max_length=500, description="取消原因")


class SubscriptionListResponse(BaseModel):
    """订阅列表响应"""
    items: List[UserSubscriptionResponse]
    total: int
    skip: int
    limit: int
