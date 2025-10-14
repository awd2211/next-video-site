"""AI 请求日志、配额、模板管理 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from typing import Optional, List
from datetime import datetime, timedelta

from app.database import get_db
from app.models.ai_log import AIRequestLog, AIQuota, AITemplate, AIPerformanceMetric
from app.schemas.ai_log import (
    AIRequestLogResponse,
    AIRequestLogQuery,
    AIQuotaCreate,
    AIQuotaUpdate,
    AIQuotaResponse,
    AITemplateCreate,
    AITemplateUpdate,
    AITemplateResponse,
    AIPerformanceMetricResponse,
    AIUsageStats,
    AICostStats,
    AIQuotaStatus,
)
from app.utils.dependencies import get_current_admin_user
from app.models.user import AdminUser

router = APIRouter(prefix="/ai-logs", tags=["AI Logs & Management"])


# ============= AI Request Logs =============

@router.get("/request-logs", response_model=dict)
async def get_request_logs(
    provider_type: Optional[str] = None,
    model: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取 AI 请求日志列表"""
    query = select(AIRequestLog)

    # 筛选条件
    conditions = []
    if provider_type:
        conditions.append(AIRequestLog.provider_type == provider_type)
    if model:
        conditions.append(AIRequestLog.model == model)
    if status:
        conditions.append(AIRequestLog.status == status)
    if start_date:
        conditions.append(AIRequestLog.created_at >= start_date)
    if end_date:
        conditions.append(AIRequestLog.created_at <= end_date)

    if conditions:
        query = query.where(and_(*conditions))

    # 总数
    count_query = select(func.count()).select_from(AIRequestLog)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页
    query = query.order_by(desc(AIRequestLog.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    logs = result.scalars().all()

    return {
        "items": [AIRequestLogResponse.from_orm(log) for log in logs],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/request-logs/{log_id}", response_model=AIRequestLogResponse)
async def get_request_log(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取单个请求日志详情"""
    result = await db.execute(select(AIRequestLog).where(AIRequestLog.id == log_id))
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=404, detail="Request log not found")

    return AIRequestLogResponse.from_orm(log)


@router.delete("/request-logs/{log_id}")
async def delete_request_log(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """删除请求日志"""
    result = await db.execute(select(AIRequestLog).where(AIRequestLog.id == log_id))
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=404, detail="Request log not found")

    await db.delete(log)
    await db.commit()

    return {"message": "Request log deleted successfully"}


# ============= AI Usage Statistics =============

@router.get("/stats/usage", response_model=AIUsageStats)
async def get_usage_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取 AI 使用统计"""
    # 默认查询最近30天
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()

    # 总请求数
    total_requests_result = await db.execute(
        select(func.count(AIRequestLog.id)).where(
            and_(
                AIRequestLog.created_at >= start_date,
                AIRequestLog.created_at <= end_date,
            )
        )
    )
    total_requests = total_requests_result.scalar() or 0

    # 总 Token 数
    total_tokens_result = await db.execute(
        select(func.sum(AIRequestLog.total_tokens)).where(
            and_(
                AIRequestLog.created_at >= start_date,
                AIRequestLog.created_at <= end_date,
            )
        )
    )
    total_tokens = total_tokens_result.scalar() or 0

    # 总成本
    total_cost_result = await db.execute(
        select(func.sum(AIRequestLog.estimated_cost)).where(
            and_(
                AIRequestLog.created_at >= start_date,
                AIRequestLog.created_at <= end_date,
            )
        )
    )
    total_cost = total_cost_result.scalar() or 0

    # 平均响应时间
    avg_response_time_result = await db.execute(
        select(func.avg(AIRequestLog.response_time)).where(
            and_(
                AIRequestLog.created_at >= start_date,
                AIRequestLog.created_at <= end_date,
            )
        )
    )
    avg_response_time = avg_response_time_result.scalar() or 0

    # 成功率
    success_count_result = await db.execute(
        select(func.count(AIRequestLog.id)).where(
            and_(
                AIRequestLog.created_at >= start_date,
                AIRequestLog.created_at <= end_date,
                AIRequestLog.status == "success",
            )
        )
    )
    success_count = success_count_result.scalar() or 0
    success_rate = (success_count / total_requests * 100) if total_requests > 0 else 0

    # 按提供商统计
    by_provider_result = await db.execute(
        select(
            AIRequestLog.provider_type,
            func.count(AIRequestLog.id).label("requests"),
            func.sum(AIRequestLog.total_tokens).label("tokens"),
            func.sum(AIRequestLog.estimated_cost).label("cost"),
        )
        .where(
            and_(
                AIRequestLog.created_at >= start_date,
                AIRequestLog.created_at <= end_date,
            )
        )
        .group_by(AIRequestLog.provider_type)
    )

    requests_by_provider = {}
    tokens_by_provider = {}
    cost_by_provider = {}

    for row in by_provider_result:
        requests_by_provider[row.provider_type] = row.requests
        tokens_by_provider[row.provider_type] = row.tokens or 0
        cost_by_provider[row.provider_type] = float(row.cost or 0)

    return AIUsageStats(
        total_requests=total_requests,
        total_tokens=total_tokens,
        total_cost=float(total_cost),
        avg_response_time=float(avg_response_time),
        success_rate=float(success_rate),
        requests_by_provider=requests_by_provider,
        tokens_by_provider=tokens_by_provider,
        cost_by_provider=cost_by_provider,
    )


@router.get("/stats/cost", response_model=AICostStats)
async def get_cost_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取成本统计"""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)

    # 今日成本
    today_cost_result = await db.execute(
        select(func.sum(AIRequestLog.estimated_cost)).where(
            AIRequestLog.created_at >= today_start
        )
    )
    today_cost = float(today_cost_result.scalar() or 0)

    # 昨日成本
    yesterday_cost_result = await db.execute(
        select(func.sum(AIRequestLog.estimated_cost)).where(
            and_(
                AIRequestLog.created_at >= yesterday_start,
                AIRequestLog.created_at < today_start,
            )
        )
    )
    yesterday_cost = float(yesterday_cost_result.scalar() or 0)

    # 本月成本
    this_month_cost_result = await db.execute(
        select(func.sum(AIRequestLog.estimated_cost)).where(
            AIRequestLog.created_at >= this_month_start
        )
    )
    this_month_cost = float(this_month_cost_result.scalar() or 0)

    # 上月成本
    last_month_cost_result = await db.execute(
        select(func.sum(AIRequestLog.estimated_cost)).where(
            and_(
                AIRequestLog.created_at >= last_month_start,
                AIRequestLog.created_at < this_month_start,
            )
        )
    )
    last_month_cost = float(last_month_cost_result.scalar() or 0)

    # 最近30天每日成本趋势
    cost_trend = []
    for i in range(30):
        day_start = today_start - timedelta(days=i)
        day_end = day_start + timedelta(days=1)

        day_cost_result = await db.execute(
            select(func.sum(AIRequestLog.estimated_cost)).where(
                and_(
                    AIRequestLog.created_at >= day_start,
                    AIRequestLog.created_at < day_end,
                )
            )
        )
        day_cost = float(day_cost_result.scalar() or 0)

        cost_trend.append(
            {"date": day_start.strftime("%Y-%m-%d"), "cost": day_cost}
        )

    cost_trend.reverse()

    # 按模型统计成本
    cost_by_model_result = await db.execute(
        select(
            AIRequestLog.model, func.sum(AIRequestLog.estimated_cost).label("cost")
        )
        .where(AIRequestLog.created_at >= this_month_start)
        .group_by(AIRequestLog.model)
    )

    cost_by_model = {}
    for row in cost_by_model_result:
        cost_by_model[row.model] = float(row.cost or 0)

    # 预计本月成本（根据已用天数推算）
    days_passed = (now - this_month_start).days + 1
    days_in_month = (
        (this_month_start.replace(month=this_month_start.month % 12 + 1, day=1) - timedelta(days=1)).day
        if this_month_start.month < 12
        else 31
    )
    projected_monthly_cost = (
        (this_month_cost / days_passed) * days_in_month if days_passed > 0 else 0
    )

    return AICostStats(
        today_cost=today_cost,
        yesterday_cost=yesterday_cost,
        this_month_cost=this_month_cost,
        last_month_cost=last_month_cost,
        cost_trend=cost_trend,
        cost_by_model=cost_by_model,
        projected_monthly_cost=projected_monthly_cost,
    )


# ============= AI Quotas =============

@router.get("/quotas", response_model=List[AIQuotaResponse])
async def get_quotas(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取所有配额设置"""
    result = await db.execute(select(AIQuota))
    quotas = result.scalars().all()
    return [AIQuotaResponse.from_orm(q) for q in quotas]


@router.post("/quotas", response_model=AIQuotaResponse)
async def create_quota(
    quota: AIQuotaCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """创建配额设置"""
    db_quota = AIQuota(**quota.dict())
    db.add(db_quota)
    await db.commit()
    await db.refresh(db_quota)
    return AIQuotaResponse.from_orm(db_quota)


@router.put("/quotas/{quota_id}", response_model=AIQuotaResponse)
async def update_quota(
    quota_id: int,
    quota_update: AIQuotaUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """更新配额设置"""
    result = await db.execute(select(AIQuota).where(AIQuota.id == quota_id))
    db_quota = result.scalar_one_or_none()

    if not db_quota:
        raise HTTPException(status_code=404, detail="Quota not found")

    for field, value in quota_update.dict(exclude_unset=True).items():
        setattr(db_quota, field, value)

    await db.commit()
    await db.refresh(db_quota)
    return AIQuotaResponse.from_orm(db_quota)


@router.delete("/quotas/{quota_id}")
async def delete_quota(
    quota_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """删除配额设置"""
    result = await db.execute(select(AIQuota).where(AIQuota.id == quota_id))
    db_quota = result.scalar_one_or_none()

    if not db_quota:
        raise HTTPException(status_code=404, detail="Quota not found")

    await db.delete(db_quota)
    await db.commit()
    return {"message": "Quota deleted successfully"}


@router.get("/quotas/status/global", response_model=AIQuotaStatus)
async def get_global_quota_status(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取全局配额使用状态"""
    result = await db.execute(
        select(AIQuota).where(
            and_(AIQuota.quota_type == "global", AIQuota.is_active == True)
        )
    )
    quota = result.scalar_one_or_none()

    if not quota:
        return AIQuotaStatus(
            quota_type="global",
            daily_limit=None,
            daily_used=0,
            daily_remaining=None,
            monthly_limit=None,
            monthly_used=0,
            monthly_remaining=None,
            is_exceeded=False,
            warning_level="normal",
        )

    daily_remaining = (
        quota.daily_request_limit - quota.daily_requests_used
        if quota.daily_request_limit
        else None
    )
    monthly_remaining = (
        quota.monthly_request_limit - quota.monthly_requests_used
        if quota.monthly_request_limit
        else None
    )

    # 判断是否超额
    is_exceeded = False
    if quota.daily_request_limit and quota.daily_requests_used >= quota.daily_request_limit:
        is_exceeded = True
    if quota.monthly_request_limit and quota.monthly_requests_used >= quota.monthly_request_limit:
        is_exceeded = True

    # 警告级别
    warning_level = "normal"
    if quota.daily_request_limit:
        usage_percent = quota.daily_requests_used / quota.daily_request_limit * 100
        if usage_percent >= 90:
            warning_level = "critical"
        elif usage_percent >= 70:
            warning_level = "warning"

    return AIQuotaStatus(
        quota_type="global",
        daily_limit=quota.daily_request_limit,
        daily_used=quota.daily_requests_used,
        daily_remaining=daily_remaining,
        monthly_limit=quota.monthly_request_limit,
        monthly_used=quota.monthly_requests_used,
        monthly_remaining=monthly_remaining,
        is_exceeded=is_exceeded,
        warning_level=warning_level,
    )


# ============= AI Templates =============

@router.get("/templates", response_model=List[AITemplateResponse])
async def get_templates(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取 AI 模板列表"""
    query = select(AITemplate)

    conditions = []
    if category:
        conditions.append(AITemplate.category == category)
    if is_active is not None:
        conditions.append(AITemplate.is_active == is_active)

    if conditions:
        query = query.where(and_(*conditions))

    query = query.order_by(desc(AITemplate.created_at))

    result = await db.execute(query)
    templates = result.scalars().all()

    return [AITemplateResponse.from_orm(t) for t in templates]


@router.post("/templates", response_model=AITemplateResponse)
async def create_template(
    template: AITemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """创建 AI 模板"""
    db_template = AITemplate(**template.dict(), created_by=current_admin.id)
    db.add(db_template)
    await db.commit()
    await db.refresh(db_template)
    return AITemplateResponse.from_orm(db_template)


@router.put("/templates/{template_id}", response_model=AITemplateResponse)
async def update_template(
    template_id: int,
    template_update: AITemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """更新 AI 模板"""
    result = await db.execute(select(AITemplate).where(AITemplate.id == template_id))
    db_template = result.scalar_one_or_none()

    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")

    for field, value in template_update.dict(exclude_unset=True).items():
        setattr(db_template, field, value)

    await db.commit()
    await db.refresh(db_template)
    return AITemplateResponse.from_orm(db_template)


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """删除 AI 模板"""
    result = await db.execute(select(AITemplate).where(AITemplate.id == template_id))
    db_template = result.scalar_one_or_none()

    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")

    await db.delete(db_template)
    await db.commit()
    return {"message": "Template deleted successfully"}
