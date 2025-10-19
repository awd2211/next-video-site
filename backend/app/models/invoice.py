"""
发票系统数据模型
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.payment import Payment
    from app.models.user import User


class InvoiceStatus(str, Enum):
    """发票状态"""
    DRAFT = "draft"        # 草稿
    PENDING = "pending"    # 待支付
    PAID = "paid"          # 已支付
    VOID = "void"          # 已作废


class Invoice(Base):
    """
    发票表

    自动生成PDF发票
    """

    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 关联关系
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    payment_id: Mapped[Optional[int]] = mapped_column(Integer, index=True, comment="关联支付")

    # 发票编号
    invoice_number: Mapped[str] = mapped_column(String(100), unique=True, index=True, comment="发票编号")

    # 状态
    status: Mapped[InvoiceStatus] = mapped_column(
        SQLEnum(InvoiceStatus),
        default=InvoiceStatus.PENDING,
        index=True,
        comment="发票状态"
    )

    # 金额
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, comment="小计")
    tax: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, comment="税费")
    discount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, comment="折扣")
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, comment="总计")
    currency: Mapped[str] = mapped_column(String(3), default="USD", comment="货币")

    # 账单信息
    billing_name: Mapped[str] = mapped_column(String(200), nullable=False, comment="账单名称")
    billing_email: Mapped[str] = mapped_column(String(255), nullable=False, comment="账单邮箱")
    billing_address: Mapped[Optional[str]] = mapped_column(Text, comment="账单地址")
    tax_id: Mapped[Optional[str]] = mapped_column(String(100), comment="税号")

    # 发票详情
    description: Mapped[Optional[str]] = mapped_column(Text, comment="描述")
    items: Mapped[Optional[str]] = mapped_column(Text, comment="项目列表 JSON")

    # PDF文件
    pdf_url: Mapped[Optional[str]] = mapped_column(String(500), comment="PDF URL")

    # 时间
    issue_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, comment="开具日期")
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="到期日期")
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="支付时间")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user: Mapped[User] = relationship("User", back_populates="invoices")
    payment: Mapped[Optional[Payment]] = relationship("Payment", back_populates="invoice")
