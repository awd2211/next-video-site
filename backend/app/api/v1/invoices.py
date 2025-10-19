"""
发票系统 API

用户端发票管理端点
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    InvoiceListResponse,
    InvoiceDownloadResponse,
)
from app.services.invoice_service import InvoiceService
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice_data: InvoiceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    创建发票

    用户可以为已支付的订单创建发票
    """
    service = InvoiceService(db)

    try:
        invoice = await service.create_invoice(
            user_id=current_user.id,
            invoice_data=invoice_data,
        )
        return invoice
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=InvoiceListResponse)
async def list_my_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的发票列表"""
    service = InvoiceService(db)
    invoices, total = await service.list_user_invoices(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )

    return InvoiceListResponse(
        items=invoices,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定发票详情"""
    service = InvoiceService(db)
    invoice = await service.get_invoice(current_user.id, invoice_id)

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    return invoice


@router.get("/number/{invoice_number}", response_model=InvoiceResponse)
async def get_invoice_by_number(
    invoice_number: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """根据发票编号获取发票"""
    service = InvoiceService(db)
    invoice = await service.get_invoice_by_number(current_user.id, invoice_number)

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    return invoice


@router.patch("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    update_data: InvoiceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新发票信息

    只能更新草稿或待支付状态的发票
    """
    service = InvoiceService(db)

    try:
        invoice = await service.update_invoice(
            user_id=current_user.id,
            invoice_id=invoice_id,
            update_data=update_data,
        )
        return invoice
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{invoice_id}/void", response_model=InvoiceResponse)
async def void_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    作废发票

    不能作废已支付的发票
    """
    service = InvoiceService(db)

    try:
        invoice = await service.void_invoice(current_user.id, invoice_id)
        return invoice
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{invoice_id}/generate-pdf", response_model=InvoiceDownloadResponse)
async def generate_invoice_pdf(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    生成发票 PDF

    返回 PDF 文件的下载链接
    """
    service = InvoiceService(db)

    # 验证发票所有权
    invoice = await service.get_invoice(current_user.id, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    try:
        pdf_url = await service.generate_pdf(invoice_id)
        return InvoiceDownloadResponse(
            pdf_url=pdf_url,
            invoice_number=invoice.invoice_number,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}",
        )


@router.post("/{invoice_id}/download")
async def download_invoice_pdf(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    下载发票 PDF

    如果还没有生成，先生成再返回下载链接
    """
    service = InvoiceService(db)

    # 验证发票所有权
    invoice = await service.get_invoice(current_user.id, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    # 如果还没有 PDF，先生成
    if not invoice.pdf_url:
        try:
            await service.generate_pdf(invoice_id)
            # 刷新 invoice 对象
            await db.refresh(invoice)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate PDF: {str(e)}",
            )

    # 重定向到 PDF URL
    if invoice.pdf_url:
        return RedirectResponse(url=invoice.pdf_url)
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PDF generation failed",
        )


@router.post("/{invoice_id}/send-email")
async def send_invoice_email(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    发送发票邮件

    将发票 PDF 发送到用户邮箱
    """
    service = InvoiceService(db)

    # 验证发票所有权
    invoice = await service.get_invoice(current_user.id, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    # 如果还没有 PDF，先生成
    if not invoice.pdf_url:
        try:
            await service.generate_pdf(invoice_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate PDF: {str(e)}",
            )

    try:
        success = await service.send_invoice_email(invoice_id)
        if success:
            return {"success": True, "message": "Invoice email sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email",
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
