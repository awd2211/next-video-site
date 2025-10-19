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


class RefundRequest(BaseModel):
    """退款请求"""
    payment_id: int = Field(..., description="支付ID")
    amount: Optional[Decimal] = Field(None, gt=0, description="退款金额 (None表示全额退款)")
    reason: Optional[str] = Field(None, max_length=500, description="退款原因")


class RefundResponse(BaseModel):
    """退款响应"""
    success: bool
    refund_id: Optional[str] = None
    amount: Optional[Decimal] = None
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
