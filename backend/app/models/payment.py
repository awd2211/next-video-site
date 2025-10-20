"""
支付系统数据模型

包含支付记录(Payment)和支付方式(PaymentMethod)
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
    from app.models.invoice import Invoice
    from app.models.subscription import UserSubscription
    from app.models.user import User


class PaymentProvider(str, Enum):
    """支付提供商"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    ALIPAY = "alipay"


class PaymentStatus(str, Enum):
    """支付状态"""
    PENDING = "pending"          # 待支付
    PROCESSING = "processing"    # 处理中
    SUCCEEDED = "succeeded"      # 成功
    FAILED = "failed"            # 失败
    CANCELED = "canceled"        # 已取消
    REFUNDED = "refunded"        # 已退款
    PARTIALLY_REFUNDED = "partially_refunded"  # 部分退款


class PaymentType(str, Enum):
    """支付类型"""
    SUBSCRIPTION = "subscription"    # 订阅支付
    RENEWAL = "renewal"              # 续费支付
    UPGRADE = "upgrade"              # 升级支付
    ONE_TIME = "one_time"            # 一次性支付


class Currency(str, Enum):
    """货币类型"""
    USD = "USD"
    CNY = "CNY"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"


class RefundReason(str, Enum):
    """退款原因"""
    USER_REQUEST = "user_request"        # 用户申请
    SERVICE_QUALITY = "service_quality"  # 服务质量问题
    TECHNICAL_ISSUE = "technical_issue"  # 技术故障
    DUPLICATE_PAYMENT = "duplicate_payment"  # 重复支付
    FRAUD = "fraud"                      # 欺诈订单
    OTHER = "other"                      # 其他原因


class RefundRequestStatus(str, Enum):
    """退款申请状态"""
    PENDING = "pending"                # 待审批
    FIRST_APPROVED = "first_approved"  # 一审通过
    APPROVED = "approved"              # 审批通过（二审通过）
    REJECTED = "rejected"              # 审批拒绝
    PROCESSING = "processing"          # 处理中
    COMPLETED = "completed"            # 已完成
    FAILED = "failed"                  # 退款失败


class Payment(Base):
    """
    支付记录表

    记录所有支付交易
    """

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 关联关系
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subscription_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("user_subscriptions.id"),
        index=True,
        comment="关联订阅"
    )

    # 支付提供商
    provider: Mapped[PaymentProvider] = mapped_column(
        SQLEnum(PaymentProvider),
        nullable=False,
        index=True,
        comment="支付提供商"
    )
    provider_payment_id: Mapped[str] = mapped_column(String(255), unique=True, comment="第三方支付ID")
    provider_customer_id: Mapped[Optional[str]] = mapped_column(String(255), comment="第三方客户ID")

    # 支付信息
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, comment="支付金额")
    currency: Mapped[Currency] = mapped_column(SQLEnum(Currency), default=Currency.USD, comment="货币类型")
    status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(PaymentStatus),
        default=PaymentStatus.PENDING,
        index=True,
        comment="支付状态"
    )
    payment_type: Mapped[PaymentType] = mapped_column(SQLEnum(PaymentType), nullable=False, comment="支付类型")

    # 退款信息
    refund_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, comment="退款金额")
    refund_reason: Mapped[Optional[str]] = mapped_column(Text, comment="退款原因")
    refunded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="退款时间")

    # 支付详情
    description: Mapped[Optional[str]] = mapped_column(String(500), comment="支付描述")
    receipt_url: Mapped[Optional[str]] = mapped_column(String(500), comment="收据URL")
    invoice_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("invoices.id"), comment="发票ID")

    # 失败信息
    failure_code: Mapped[Optional[str]] = mapped_column(String(100), comment="失败代码")
    failure_message: Mapped[Optional[str]] = mapped_column(Text, comment="失败消息")

    # 元数据
    extra_metadata: Mapped[Optional[str]] = mapped_column(Text, comment="额外元数据 JSON")

    # 时间戳
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="支付完成时间")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user: Mapped[User] = relationship("User", back_populates="payments")
    subscription: Mapped[Optional[UserSubscription]] = relationship("UserSubscription", back_populates="payments")
    invoice: Mapped[Optional[Invoice]] = relationship("Invoice", back_populates="payment")
    refund_requests: Mapped[list["RefundRequest"]] = relationship("RefundRequest", back_populates="payment", foreign_keys="[RefundRequest.payment_id]")


class PaymentMethod(Base):
    """
    用户支付方式表

    保存用户的支付方式（加密的令牌，不存储敏感信息）
    """

    __tablename__ = "payment_methods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 关联用户
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 支付提供商
    provider: Mapped[PaymentProvider] = mapped_column(SQLEnum(PaymentProvider), nullable=False, comment="支付提供商")
    provider_payment_method_id: Mapped[str] = mapped_column(String(255), comment="第三方支付方式ID")

    # 支付方式详情（不包含敏感信息）
    type: Mapped[str] = mapped_column(String(50), comment="类型: card, paypal, alipay")
    card_brand: Mapped[Optional[str]] = mapped_column(String(50), comment="卡品牌: visa, mastercard, etc.")
    card_last4: Mapped[Optional[str]] = mapped_column(String(4), comment="卡号后4位")
    card_exp_month: Mapped[Optional[int]] = mapped_column(Integer, comment="过期月份")
    card_exp_year: Mapped[Optional[int]] = mapped_column(Integer, comment="过期年份")

    # 状态
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否为默认支付方式")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user: Mapped[User] = relationship("User", back_populates="payment_methods")


class RefundRequest(Base):
    """
    退款申请表

    实现双重审批机制的退款流程
    """

    __tablename__ = "refund_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 关联关系
    payment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("payments.id"),
        nullable=False,
        index=True,
        comment="关联支付记录"
    )
    requested_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("admin_users.id"),
        nullable=False,
        comment="申请人（管理员ID）"
    )
    first_approver_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("admin_users.id"),
        comment="一审审批人ID"
    )
    second_approver_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("admin_users.id"),
        comment="二审审批人ID"
    )

    # 退款信息
    refund_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="申请退款金额"
    )
    refund_reason: Mapped[RefundReason] = mapped_column(
        SQLEnum(RefundReason),
        nullable=False,
        index=True,
        comment="退款原因类别"
    )
    reason_detail: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="退款原因详细说明"
    )
    admin_note: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="管理员内部备注"
    )

    # 审批状态
    status: Mapped[RefundRequestStatus] = mapped_column(
        SQLEnum(RefundRequestStatus),
        default=RefundRequestStatus.PENDING,
        nullable=False,
        index=True,
        comment="审批状态"
    )

    # 审批记录
    first_approval_note: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="一审审批意见"
    )
    first_approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        comment="一审通过时间"
    )

    second_approval_note: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="二审审批意见"
    )
    second_approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        comment="二审通过时间"
    )

    rejection_note: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="拒绝原因"
    )
    rejected_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        comment="拒绝时间"
    )

    # 处理结果
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        comment="实际处理时间"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        comment="完成时间"
    )
    failure_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="失败原因"
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
        comment="创建时间"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment="更新时间"
    )

    # 关系（使用字符串避免循环导入）
    payment: Mapped["Payment"] = relationship("Payment", foreign_keys=[payment_id])
    requester: Mapped["AdminUser"] = relationship("AdminUser", foreign_keys=[requested_by])
    first_approver: Mapped[Optional["AdminUser"]] = relationship("AdminUser", foreign_keys=[first_approver_id])
    second_approver: Mapped[Optional["AdminUser"]] = relationship("AdminUser", foreign_keys=[second_approver_id])
