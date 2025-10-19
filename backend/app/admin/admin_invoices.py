"""
管理端 - 发票管理 API

管理员可以查看所有发票、生成报表、导出财务数据
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_

from app.database import get_db
from app.models.user import AdminUser
from app.models.invoice import Invoice, InvoiceStatus
from app.schemas.invoice import (
    InvoiceResponse,
    InvoiceListResponse,
    InvoiceUpdate,
)
from app.services.invoice_service import InvoiceService
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


@router.get("/", response_model=InvoiceListResponse)
async def list_all_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[InvoiceStatus] = Query(None, description="Filter by status"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取所有发票

    管理员可以查看所有用户的发票记录
    """
    query = select(Invoice)

    # 应用筛选条件
    conditions = []
    if status_filter:
        conditions.append(Invoice.status == status_filter)
    if user_id:
        conditions.append(Invoice.user_id == user_id)
    if start_date:
        conditions.append(Invoice.created_at >= start_date)
    if end_date:
        conditions.append(Invoice.created_at <= end_date)

    if conditions:
        query = query.where(and_(*conditions))

    # 查询总数
    count_result = await db.execute(query)
    total = len(list(count_result.scalars().all()))

    # 查询列表
    result = await db.execute(
        query.order_by(desc(Invoice.created_at)).offset(skip).limit(limit)
    )
    invoices = list(result.scalars().all())

    return InvoiceListResponse(
        items=invoices,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定发票详情"""
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    return invoice


@router.patch("/{invoice_id}", response_model=InvoiceResponse)
async def admin_update_invoice(
    invoice_id: int,
    update_data: InvoiceUpdate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    管理员更新发票

    管理员可以更新任何状态的发票
    """
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    # 更新字段
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(invoice, field, value)

    await db.commit()
    await db.refresh(invoice)

    return invoice


@router.post("/{invoice_id}/mark-paid", response_model=InvoiceResponse)
async def mark_invoice_paid(
    invoice_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """标记发票为已支付"""
    service = InvoiceService(db)

    try:
        invoice = await service.mark_as_paid(invoice_id)
        return invoice
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/{invoice_id}/void", response_model=InvoiceResponse)
async def void_invoice(
    invoice_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """作废发票"""
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    invoice.status = InvoiceStatus.VOID
    await db.commit()
    await db.refresh(invoice)

    return invoice


@router.get("/stats/financial", response_model=dict)
async def get_financial_statistics(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取财务统计数据

    返回发票总额、已支付金额、待支付金额等财务指标
    """
    service = InvoiceService(db)
    stats = await service.calculate_statistics(start_date, end_date)

    return stats


@router.get("/user/{user_id}/invoices", response_model=InvoiceListResponse)
async def get_user_invoices(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取指定用户的所有发票

    管理员可以查看任何用户的发票历史
    """
    service = InvoiceService(db)
    invoices, total = await service.list_user_invoices(
        user_id=user_id,
        skip=skip,
        limit=limit,
    )

    return InvoiceListResponse(
        items=invoices,
        total=total,
        skip=skip,
        limit=limit,
    )
