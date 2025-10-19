"""
发票系统 Pydantic Schemas
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

from app.models.invoice import InvoiceStatus


class InvoiceBase(BaseModel):
    """发票基础 Schema"""
    billing_name: str = Field(..., min_length=1, max_length=200, description="账单名称")
    billing_email: EmailStr = Field(..., description="账单邮箱")
    billing_address: Optional[str] = Field(None, description="账单地址")
    tax_id: Optional[str] = Field(None, max_length=100, description="税号")


class InvoiceCreate(InvoiceBase):
    """创建发票"""
    payment_id: int = Field(..., description="关联支付ID")
    subtotal: Decimal = Field(..., gt=0, description="小计")
    tax: Decimal = Field(default=0, ge=0, description="税费")
    discount: Decimal = Field(default=0, ge=0, description="折扣")
    currency: str = Field(default="USD", max_length=3, description="货币")
    description: Optional[str] = Field(None, description="描述")
    items: Optional[str] = Field(None, description="项目列表 JSON")


class InvoiceUpdate(BaseModel):
    """更新发票"""
    status: Optional[InvoiceStatus] = None
    billing_name: Optional[str] = Field(None, min_length=1, max_length=200)
    billing_email: Optional[EmailStr] = None
    billing_address: Optional[str] = None
    tax_id: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class InvoiceResponse(BaseModel):
    """发票响应"""
    id: int
    user_id: int
    payment_id: Optional[int] = None

    invoice_number: str
    status: InvoiceStatus

    subtotal: Decimal
    tax: Decimal
    discount: Decimal
    total: Decimal
    currency: str

    billing_name: str
    billing_email: str
    billing_address: Optional[str] = None
    tax_id: Optional[str] = None

    description: Optional[str] = None
    items: Optional[str] = None

    pdf_url: Optional[str] = None

    issue_date: datetime
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    """发票列表响应"""
    items: List[InvoiceResponse]
    total: int
    skip: int
    limit: int


class InvoiceGenerateRequest(BaseModel):
    """生成发票请求"""
    payment_id: int = Field(..., description="支付ID")
    billing_info: InvoiceBase


class InvoiceDownloadResponse(BaseModel):
    """下载发票响应"""
    pdf_url: str = Field(..., description="PDF URL")
    invoice_number: str = Field(..., description="发票编号")
