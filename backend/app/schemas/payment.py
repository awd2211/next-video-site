"""
支付系统 Pydantic Schemas
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

from app.models.payment import (
    PaymentProvider,
    PaymentStatus,
    PaymentType,
    Currency,
    RefundReason,
    RefundRequestStatus,
)


# ==================== Payment Schemas ====================

class PaymentBase(BaseModel):
    """支付基础 Schema"""
    amount: Decimal = Field(..., gt=0, description="支付金额")
    currency: Currency = Field(default=Currency.USD, description="货币类型")
    description: Optional[str] = Field(None, max_length=500, description="支付描述")


class PaymentCreate(PaymentBase):
    """创建支付"""
    provider: PaymentProvider = Field(..., description="支付提供商")
    payment_type: PaymentType = Field(..., description="支付类型")
    subscription_id: Optional[int] = Field(None, description="关联订阅ID")
    payment_method_id: Optional[str] = Field(None, description="支付方式ID")


class PaymentResponse(BaseModel):
    """支付响应"""
    id: int
    user_id: int
    subscription_id: Optional[int] = None

    provider: PaymentProvider
    provider_payment_id: str
    provider_customer_id: Optional[str] = None

    amount: Decimal
    currency: Currency
    status: PaymentStatus
    payment_type: PaymentType

    refund_amount: Decimal
    refund_reason: Optional[str] = None
    refunded_at: Optional[datetime] = None

    description: Optional[str] = None
    receipt_url: Optional[str] = None

    failure_code: Optional[str] = None
    failure_message: Optional[str] = None

    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaymentIntentRequest(BaseModel):
    """创建支付意图请求"""
    amount: Decimal = Field(..., gt=0, description="支付金额")
    currency: Currency = Field(default=Currency.USD, description="货币")
    provider: PaymentProvider = Field(..., description="支付提供商")
    payment_method_id: Optional[str] = Field(None, description="支付方式ID")
    description: Optional[str] = Field(None, max_length=500, description="支付描述")


class PaymentIntentResponse(BaseModel):
    """支付意图响应"""
    success: bool
    payment_id: Optional[int] = None
    provider_payment_id: Optional[str] = None
    client_secret: Optional[str] = None
    payment_url: Optional[str] = None
    status: Optional[str] = None
    failure_message: Optional[str] = None


class PaymentConfirmRequest(BaseModel):
    """确认支付请求"""
    payment_id: int = Field(..., description="支付ID")
    payment_method_id: Optional[str] = Field(None, description="支付方式ID")


class DirectRefundRequest(BaseModel):
    """直接退款请求（旧系统，仅用于兼容）"""
    payment_id: int = Field(..., description="支付ID")
    amount: Optional[Decimal] = Field(None, gt=0, description="退款金额 (None表示全额退款)")
    reason: Optional[RefundReason] = Field(None, description="退款原因类别")
    reason_detail: Optional[str] = Field(None, max_length=500, description="退款原因详细说明")
    admin_note: Optional[str] = Field(None, max_length=1000, description="管理员内部备注")


# ==================== RefundRequest Schemas (审批流程) ====================

class RefundRequestCreate(BaseModel):
    """创建退款审批申请"""
    payment_id: int = Field(..., description="支付ID")
    refund_amount: Decimal = Field(..., gt=0, description="申请退款金额")
    refund_reason: RefundReason = Field(..., description="退款原因类别")
    reason_detail: Optional[str] = Field(None, max_length=500, description="退款原因详细说明")
    admin_note: Optional[str] = Field(None, max_length=1000, description="管理员内部备注")


class RefundRequestUpdate(BaseModel):
    """更新退款审批申请"""
    refund_amount: Optional[Decimal] = Field(None, gt=0, description="申请退款金额")
    refund_reason: Optional[RefundReason] = Field(None, description="退款原因类别")
    reason_detail: Optional[str] = Field(None, max_length=500, description="退款原因详细说明")
    admin_note: Optional[str] = Field(None, max_length=1000, description="管理员内部备注")


class RefundRequestApprove(BaseModel):
    """审批退款申请"""
    approval_note: str = Field(..., max_length=1000, description="审批意见")


class RefundRequestReject(BaseModel):
    """拒绝退款申请"""
    rejection_note: str = Field(..., max_length=1000, description="拒绝原因")


class RefundRequestResponse(BaseModel):
    """退款审批申请响应"""
    id: int
    payment_id: int
    requested_by: int
    first_approver_id: Optional[int] = None
    second_approver_id: Optional[int] = None

    refund_amount: Decimal
    refund_reason: RefundReason
    reason_detail: Optional[str] = None
    admin_note: Optional[str] = None

    status: RefundRequestStatus

    first_approval_note: Optional[str] = None
    first_approved_at: Optional[datetime] = None

    second_approval_note: Optional[str] = None
    second_approved_at: Optional[datetime] = None

    rejection_note: Optional[str] = None
    rejected_at: Optional[datetime] = None

    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RefundRequestWithDetails(RefundRequestResponse):
    """退款审批申请详情（包含关联信息）"""
    payment: Optional[PaymentResponse] = None
    requester: Optional[dict] = None  # AdminUser 信息
    first_approver: Optional[dict] = None
    second_approver: Optional[dict] = None


class RefundRequestListResponse(BaseModel):
    """退款审批申请列表响应"""
    items: List[RefundRequestResponse]
    total: int


class RefundResponse(BaseModel):
    """退款响应"""
    success: bool
    refund_id: Optional[str] = None
    amount: Optional[Decimal] = None
    total_refunded: Optional[Decimal] = None
    payment_status: Optional[str] = None
    failure_message: Optional[str] = None
    refunded_at: Optional[datetime] = None


class PaymentListResponse(BaseModel):
    """支付列表响应"""
    items: List[PaymentResponse]
    total: int
    skip: int
    limit: int


# ==================== PaymentMethod Schemas ====================

class PaymentMethodBase(BaseModel):
    """支付方式基础 Schema"""
    provider: PaymentProvider = Field(..., description="支付提供商")
    type: str = Field(..., max_length=50, description="类型: card, paypal, alipay")


class PaymentMethodCreate(PaymentMethodBase):
    """创建支付方式"""
    provider_payment_method_id: str = Field(..., max_length=255, description="第三方支付方式ID")
    card_brand: Optional[str] = Field(None, max_length=50, description="卡品牌")
    card_last4: Optional[str] = Field(None, max_length=4, description="卡号后4位")
    card_exp_month: Optional[int] = Field(None, ge=1, le=12, description="过期月份")
    card_exp_year: Optional[int] = Field(None, ge=2024, description="过期年份")
    is_default: bool = Field(default=False, description="是否为默认支付方式")


class PaymentMethodUpdate(BaseModel):
    """更新支付方式"""
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class PaymentMethodResponse(BaseModel):
    """支付方式响应"""
    id: int
    user_id: int

    provider: PaymentProvider
    provider_payment_method_id: str

    type: str
    card_brand: Optional[str] = None
    card_last4: Optional[str] = None
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None

    is_default: bool
    is_active: bool

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaymentMethodListResponse(BaseModel):
    """支付方式列表响应"""
    items: List[PaymentMethodResponse]
    total: int
