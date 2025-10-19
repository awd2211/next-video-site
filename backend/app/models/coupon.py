"""
优惠券系统数据模型
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.subscription import UserSubscription


class DiscountType(str, Enum):
    """折扣类型"""
    PERCENTAGE = "percentage"  # 百分比折扣 (如 20% off)
    FIXED_AMOUNT = "fixed_amount"  # 固定金额折扣 (如 $10 off)
    FREE_TRIAL = "free_trial"  # 免费试用延长


class CouponStatus(str, Enum):
    """优惠券状态"""
    ACTIVE = "active"
    EXPIRED = "expired"
    DISABLED = "disabled"


class Coupon(Base):
    """
    优惠券表

    支持百分比折扣、固定金额折扣和免费试用延长
    """

    __tablename__ = "coupons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 优惠券代码
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False, comment="优惠券代码")

    # 折扣信息
    discount_type: Mapped[DiscountType] = mapped_column(SQLEnum(DiscountType), nullable=False, comment="折扣类型")
    discount_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, comment="折扣值")
    max_discount_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), comment="最大折扣金额")

    # 使用限制
    usage_limit: Mapped[Optional[int]] = mapped_column(Integer, comment="总使用次数限制")
    usage_count: Mapped[int] = mapped_column(Integer, default=0, comment="已使用次数")
    usage_limit_per_user: Mapped[int] = mapped_column(Integer, default=1, comment="每个用户使用次数限制")

    # 最低消费
    minimum_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), comment="最低消费金额")

    # 适用范围
    applicable_plans: Mapped[Optional[str]] = mapped_column(Text, comment="适用套餐ID列表 JSON")

    # 有效期
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, comment="有效期开始")
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="有效期结束")

    # 状态
    status: Mapped[CouponStatus] = mapped_column(
        SQLEnum(CouponStatus),
        default=CouponStatus.ACTIVE,
        index=True,
        comment="状态"
    )
    is_first_purchase_only: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否仅限首次购买")

    # 描述
    description: Mapped[Optional[str]] = mapped_column(Text, comment="描述")

    # 创建者
    created_by: Mapped[Optional[int]] = mapped_column(Integer, comment="创建者ID (admin)")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    subscriptions: Mapped[list[UserSubscription]] = relationship("UserSubscription", back_populates="coupon")

    def is_valid(self) -> bool:
        """检查优惠券是否有效"""
        now = datetime.now()

        # 检查状态
        if self.status != CouponStatus.ACTIVE:
            return False

        # 检查有效期
        if now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False

        # 检查使用次数
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False

        return True
