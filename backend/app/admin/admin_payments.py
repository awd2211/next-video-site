"""
管理端 - 支付管理 API

管理员可以查看所有支付记录、处理退款、查看统计数据
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, func
from decimal import Decimal

from app.database import get_db
from app.models.user import AdminUser
from app.models.payment import Payment, PaymentStatus, PaymentProvider
from app.schemas.payment import (
    PaymentResponse,
    PaymentListResponse,
    RefundRequestCreate,
    RefundResponse,
)
from app.services.payment_service import PaymentService
from app.services.payment_gateway import PaymentGatewayConfig
from app.utils.dependencies import get_current_admin_user
from app.config import get_settings

router = APIRouter()
settings = get_settings()


def get_gateway_config(provider: PaymentProvider) -> PaymentGatewayConfig:
    """获取支付网关配置"""
    if provider == PaymentProvider.STRIPE:
        return PaymentGatewayConfig(
            provider=PaymentProvider.STRIPE,
            api_key=settings.STRIPE_SECRET_KEY,
            webhook_secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    elif provider == PaymentProvider.PAYPAL:
        return PaymentGatewayConfig(
            provider=PaymentProvider.PAYPAL,
            api_key=settings.PAYPAL_CLIENT_ID,
            api_secret=settings.PAYPAL_CLIENT_SECRET,
            environment=settings.PAYPAL_ENVIRONMENT,
        )
    elif provider == PaymentProvider.ALIPAY:
        return PaymentGatewayConfig(
            provider=PaymentProvider.ALIPAY,
            api_key=settings.ALIPAY_APP_ID,
            api_secret=settings.ALIPAY_PRIVATE_KEY,
            public_key=settings.ALIPAY_PUBLIC_KEY,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported payment provider: {provider}",
        )


@router.get("/", response_model=PaymentListResponse)
async def list_all_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[PaymentStatus] = Query(None, description="Filter by status"),
    provider: Optional[PaymentProvider] = Query(None, description="Filter by provider"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取所有支付记录

    管理员可以查看所有用户的支付记录，支持多种筛选条件
    """
    query = select(Payment)

    # 应用筛选条件
    conditions = []
    if status_filter:
        conditions.append(Payment.status == status_filter)
    if provider:
        conditions.append(Payment.provider == provider)
    if user_id:
        conditions.append(Payment.user_id == user_id)
    if start_date:
        conditions.append(Payment.created_at >= start_date)
    if end_date:
        conditions.append(Payment.created_at <= end_date)

    if conditions:
        query = query.where(and_(*conditions))

    # 查询总数
    count_result = await db.execute(query)
    total = len(list(count_result.scalars().all()))

    # 查询列表
    result = await db.execute(
        query.order_by(desc(Payment.created_at)).offset(skip).limit(limit)
    )
    payments = list(result.scalars().all())

    return PaymentListResponse(
        items=payments,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定支付记录详情"""
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return payment


@router.post("/{payment_id}/refund", response_model=RefundResponse)
async def admin_refund_payment(
    payment_id: int,
    refund_request: RefundRequestCreate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    管理员处理退款

    管理员可以为任何支付记录创建退款,支持部分退款和全额退款
    可以指定退款原因和管理员备注
    """
    service = PaymentService(db)

    # 获取支付记录
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    # 验证支付状态
    if payment.status not in [PaymentStatus.SUCCEEDED, PaymentStatus.PARTIALLY_REFUNDED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot refund payment with status: {payment.status}",
        )

    # 验证退款金额
    if refund_request.amount:
        remaining_amount = payment.amount - payment.refund_amount
        if refund_request.amount > remaining_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Refund amount ({refund_request.amount}) exceeds remaining amount ({remaining_amount})",
            )

    # 验证 payment_id 匹配
    if refund_request.payment_id != payment_id:
        refund_request.payment_id = payment_id

    # 构建退款原因说明
    refund_reason_parts = []
    if refund_request.reason:
        refund_reason_parts.append(f"Reason: {refund_request.reason.value}")
    if refund_request.reason_detail:
        refund_reason_parts.append(refund_request.reason_detail)
    if refund_request.admin_note:
        refund_reason_parts.append(f"(Admin note: {refund_request.admin_note})")

    # 合并退款原因用于存储
    combined_reason = " - ".join(refund_reason_parts) if refund_reason_parts else None

    gateway_config = get_gateway_config(payment.provider)

    try:
        # 创建一个包含完整原因的新request对象
        from pydantic import BaseModel
        from copy import deepcopy

        # 暂时将reason字段设为字符串以传递给服务层
        refund_data = refund_request.model_dump()
        refund_data['reason'] = combined_reason

        result = await service.create_refund(
            user_id=None,  # 管理员操作，不需要用户验证
            request=refund_request,
            gateway_config=gateway_config,
        )

        return RefundResponse(
            success=result.get("success", False),
            refund_id=result.get("refund_id"),
            amount=result.get("amount"),
            total_refunded=result.get("total_refunded"),
            payment_status=result.get("payment_status"),
            refunded_at=datetime.now() if result.get("success") else None,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Refund failed: {str(e)}",
        )


@router.get("/stats/overview", response_model=dict)
async def get_payment_statistics(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取支付统计数据

    返回总收入、支付成功率、退款率等关键指标
    """
    query = select(Payment)

    # 应用日期筛选
    if start_date:
        query = query.where(Payment.created_at >= start_date)
    if end_date:
        query = query.where(Payment.created_at <= end_date)

    result = await db.execute(query)
    payments = list(result.scalars().all())

    # 计算统计数据
    total_payments = len(payments)
    succeeded = [p for p in payments if p.status == PaymentStatus.SUCCEEDED]
    failed = [p for p in payments if p.status == PaymentStatus.FAILED]
    refunded = [
        p
        for p in payments
        if p.status in [PaymentStatus.REFUNDED, PaymentStatus.PARTIALLY_REFUNDED]
    ]

    total_revenue = sum(p.amount for p in succeeded)
    total_refunded = sum(p.refund_amount for p in payments)
    net_revenue = total_revenue - total_refunded

    success_rate = (len(succeeded) / total_payments * 100) if total_payments > 0 else 0
    refund_rate = (len(refunded) / len(succeeded) * 100) if len(succeeded) > 0 else 0

    # 按支付提供商分组
    by_provider = {}
    for provider in PaymentProvider:
        provider_payments = [p for p in succeeded if p.provider == provider]
        by_provider[provider.value] = {
            "count": len(provider_payments),
            "total_amount": float(sum(p.amount for p in provider_payments)),
        }

    return {
        "total_payments": total_payments,
        "succeeded_payments": len(succeeded),
        "failed_payments": len(failed),
        "refunded_payments": len(refunded),
        "total_revenue": float(total_revenue),
        "total_refunded": float(total_refunded),
        "net_revenue": float(net_revenue),
        "success_rate": round(success_rate, 2),
        "refund_rate": round(refund_rate, 2),
        "by_provider": by_provider,
        "period": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
        },
    }


@router.get("/stats/daily", response_model=dict)
async def get_daily_payment_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取每日支付统计

    返回指定天数的每日支付数据，用于趋势分析
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    result = await db.execute(
        select(Payment).where(
            and_(
                Payment.created_at >= start_date,
                Payment.created_at <= end_date,
                Payment.status == PaymentStatus.SUCCEEDED,
            )
        )
    )
    payments = list(result.scalars().all())

    # 按日期分组
    daily_stats = {}
    for payment in payments:
        date_key = payment.created_at.date().isoformat()
        if date_key not in daily_stats:
            daily_stats[date_key] = {"count": 0, "total_amount": Decimal(0)}

        daily_stats[date_key]["count"] += 1
        daily_stats[date_key]["total_amount"] += payment.amount

    # 转换为列表格式
    daily_list = [
        {
            "date": date,
            "count": stats["count"],
            "total_amount": float(stats["total_amount"]),
        }
        for date, stats in sorted(daily_stats.items())
    ]

    return {
        "days": days,
        "start_date": start_date.date().isoformat(),
        "end_date": end_date.date().isoformat(),
        "daily_stats": daily_list,
    }


@router.get("/user/{user_id}/payments", response_model=PaymentListResponse)
async def get_user_payments(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取指定用户的所有支付记录

    管理员可以查看任何用户的支付历史
    """
    service = PaymentService(db)
    payments, total = await service.list_user_payments(
        user_id=user_id,
        skip=skip,
        limit=limit,
    )

    return PaymentListResponse(
        items=payments,
        total=total,
        skip=skip,
        limit=limit,
    )
