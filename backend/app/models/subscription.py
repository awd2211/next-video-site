"""
订阅系统数据模型

包含订阅套餐(SubscriptionPlan)和用户订阅(UserSubscription)
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.coupon import Coupon
    from app.models.payment import Payment
    from app.models.user import User


class BillingPeriod(str, Enum):
    """计费周期"""
    MONTHLY = "monthly"        # 月付
    QUARTERLY = "quarterly"    # 季付
    YEARLY = "yearly"          # 年付
    LIFETIME = "lifetime"      # 终身


class SubscriptionStatus(str, Enum):
    """订阅状态"""
    ACTIVE = "active"          # 激活中
    TRIALING = "trialing"      # 试用中
    PAST_DUE = "past_due"      # 逾期未付
    CANCELED = "canceled"      # 已取消
    EXPIRED = "expired"        # 已过期
    INCOMPLETE = "incomplete"  # 未完成（支付失败）


class SubscriptionPlan(Base):
    """
    订阅套餐表

    定义不同等级的会员套餐，如 Basic, Standard, Premium
    """

    __tablename__ = "subscription_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 基本信息
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="套餐名称")
    name_en: Mapped[Optional[str]] = mapped_column(String(100), comment="英文名称")
    name_zh: Mapped[Optional[str]] = mapped_column(String(100), comment="中文名称")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="套餐描述")
    description_en: Mapped[Optional[str]] = mapped_column(Text, comment="英文描述")
    description_zh: Mapped[Optional[str]] = mapped_column(Text, comment="中文描述")

    # 定价
    billing_period: Mapped[BillingPeriod] = mapped_column(SQLEnum(BillingPeriod), nullable=False, comment="计费周期")
    price_usd: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, comment="美元价格")
    price_cny: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, comment="人民币价格")
    price_eur: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), comment="欧元价格")

    # 试用期
    trial_days: Mapped[int] = mapped_column(Integer, default=0, comment="试用天数")

    # 权限和限制
    features: Mapped[Optional[str]] = mapped_column(Text, comment="功能列表 JSON")
    max_video_quality: Mapped[str] = mapped_column(String(20), default="1080p", comment="最高视频质量")
    max_concurrent_streams: Mapped[int] = mapped_column(Integer, default=1, comment="最大并发播放数")
    allow_downloads: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否允许下载")
    ad_free: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否无广告")

    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否热门推荐")
    display_order: Mapped[int] = mapped_column(Integer, default=0, comment="显示顺序")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    subscriptions: Mapped[list[UserSubscription]] = relationship(
        "UserSubscription", back_populates="plan", cascade="all, delete-orphan"
    )


class UserSubscription(Base):
    """
    用户订阅表

    记录用户的订阅状态、开始时间、结束时间等
    """

    __tablename__ = "user_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 关联关系
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("subscription_plans.id"), nullable=False)

    # 订阅状态
    status: Mapped[SubscriptionStatus] = mapped_column(
        SQLEnum(SubscriptionStatus),
        default=SubscriptionStatus.ACTIVE,
        index=True,
        comment="订阅状态"
    )

    # 时间管理
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, comment="开始时间")
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, comment="结束时间")
    trial_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="试用结束时间")
    canceled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="取消时间")

    # 续费设置
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否自动续费")
    renew_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="下次续费时间")

    # 支付信息
    payment_method_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("payment_methods.id"),
        comment="默认支付方式"
    )
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, comment="Stripe 订阅ID")
    paypal_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, comment="PayPal 订阅ID")

    # 优惠
    coupon_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("coupons.id"), comment="使用的优惠券")
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, comment="折扣金额")

    # 元数据
    extra_metadata: Mapped[Optional[str]] = mapped_column(Text, comment="额外元数据 JSON")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user: Mapped[User] = relationship("User", back_populates="subscriptions")
    plan: Mapped[SubscriptionPlan] = relationship("SubscriptionPlan", back_populates="subscriptions")
    payments: Mapped[list[Payment]] = relationship("Payment", back_populates="subscription")
    coupon: Mapped[Optional["Coupon"]] = relationship("Coupon", back_populates="subscriptions")

    def is_active(self) -> bool:
        """判断订阅是否有效"""
        return self.status == SubscriptionStatus.ACTIVE and datetime.now() < self.end_date

    def is_in_trial(self) -> bool:
        """判断是否在试用期"""
        if not self.trial_end_date:
            return False
        return self.status == SubscriptionStatus.TRIALING and datetime.now() < self.trial_end_date
