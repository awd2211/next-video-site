import csv
import io
import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.admin import OperationLog
from app.models.user import AdminUser
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


async def create_operation_log(
    db: AsyncSession,
    admin_user_id: int,
    module: str,
    action: str,
    description: str,
    request: Request = None,
    request_data: dict = None,
):
    """创建操作日志的辅助函数"""
    log = OperationLog(
        admin_user_id=admin_user_id,
        module=module,
        action=action,
        description=description,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
        request_method=request.method if request else None,
        request_url=str(request.url) if request else None,
        request_data=(
            json.dumps(request_data, ensure_ascii=False) if request_data else None
        ),
    )
    db.add(log)
    await db.commit()
    return log


@router.get("/operations")
async def get_operation_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    module: str = Query(None),
    action: str = Query(None),
    admin_user_id: int = Query(None),
    search: str = Query(""),
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取操作日志列表，支持筛选和搜索"""
    query = select(OperationLog).options(selectinload(OperationLog.admin_user))

    # 筛选模块
    if module:
        query = query.filter(OperationLog.module == module)

    # 筛选操作类型
    if action:
        query = query.filter(OperationLog.action == action)

    # 筛选管理员
    if admin_user_id:
        query = query.filter(OperationLog.admin_user_id == admin_user_id)

    # 搜索描述或IP地址
    if search:
        query = query.filter(
            or_(
                OperationLog.description.ilike(f"%{search}%"),
                OperationLog.ip_address.ilike(f"%{search}%"),
            )
        )

    # 日期范围筛选
    if start_date:
        start_datetime = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        query = query.filter(OperationLog.created_at >= start_datetime)

    if end_date:
        end_datetime = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        query = query.filter(OperationLog.created_at <= end_datetime)

    # 获取总数
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    # 分页和排序
    offset = (page - 1) * page_size
    query = (
        query.order_by(desc(OperationLog.created_at)).offset(offset).limit(page_size)
    )
    result = await db.execute(query)
    logs = result.scalars().all()

    return {"total": total, "page": page, "page_size": page_size, "items": logs}


@router.get("/operations/{log_id}")
async def get_operation_log_detail(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取单个操作日志详情"""
    result = await db.execute(
        select(OperationLog)
        .options(selectinload(OperationLog.admin_user))
        .filter(OperationLog.id == log_id)
    )
    log = result.scalar_one_or_none()

    if not log:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="操作日志不存在")

    return log


@router.get("/operations/stats/summary")
async def get_operation_logs_summary(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取操作日志统计摘要"""
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    # 按模块统计
    module_stats = await db.execute(
        select(OperationLog.module, func.count(OperationLog.id).label("count"))
        .filter(OperationLog.created_at >= start_date)
        .group_by(OperationLog.module)
        .order_by(desc("count"))
    )

    # 按操作类型统计
    action_stats = await db.execute(
        select(OperationLog.action, func.count(OperationLog.id).label("count"))
        .filter(OperationLog.created_at >= start_date)
        .group_by(OperationLog.action)
        .order_by(desc("count"))
    )

    # 按管理员统计
    admin_stats = await db.execute(
        select(OperationLog.admin_user_id, func.count(OperationLog.id).label("count"))
        .filter(OperationLog.created_at >= start_date)
        .filter(OperationLog.admin_user_id.isnot(None))
        .group_by(OperationLog.admin_user_id)
        .order_by(desc("count"))
        .limit(10)
    )

    # 每日操作趋势
    daily_stats = await db.execute(
        select(
            func.date(OperationLog.created_at).label("date"),
            func.count(OperationLog.id).label("count"),
        )
        .filter(OperationLog.created_at >= start_date)
        .group_by(func.date(OperationLog.created_at))
        .order_by("date")
    )

    return {
        "module_stats": [
            {"module": row.module, "count": row.count} for row in module_stats.all()
        ],
        "action_stats": [
            {"action": row.action, "count": row.count} for row in action_stats.all()
        ],
        "admin_stats": [
            {"admin_user_id": row.admin_user_id, "count": row.count}
            for row in admin_stats.all()
        ],
        "daily_stats": [
            {"date": str(row.date), "count": row.count} for row in daily_stats.all()
        ],
    }


@router.delete("/operations/cleanup")
async def cleanup_old_logs(
    days: int = Query(90, ge=30, le=365, description="删除多少天之前的日志"),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """清理旧的操作日志"""
    # 只有超级管理员才能清理日志
    if not current_admin.is_superadmin:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="只有超级管理员才能清理日志")

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

    # 查询要删除的日志数量
    count_result = await db.execute(
        select(func.count())
        .select_from(OperationLog)
        .filter(OperationLog.created_at < cutoff_date)
    )
    delete_count = count_result.scalar()

    # 删除旧日志
    from sqlalchemy import delete as sql_delete

    await db.execute(
        sql_delete(OperationLog).filter(OperationLog.created_at < cutoff_date)
    )
    await db.commit()

    # 记录清理操作
    await create_operation_log(
        db=db,
        admin_user_id=current_admin.id,
        module="system",
        action="cleanup",
        description=f"清理了 {days} 天前的操作日志，共删除 {delete_count} 条记录",
    )

    return {
        "message": f"成功清理 {delete_count} 条日志记录",
        "deleted_count": delete_count,
        "cutoff_date": cutoff_date.isoformat(),
    }


@router.get("/operations/modules/list")
async def get_available_modules(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取所有可用的模块列表"""
    result = await db.execute(
        select(OperationLog.module).distinct().order_by(OperationLog.module)
    )
    modules = [row[0] for row in result.all()]
    return {"modules": modules}


@router.get("/operations/actions/list")
async def get_available_actions(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取所有可用的操作类型列表"""
    result = await db.execute(
        select(OperationLog.action).distinct().order_by(OperationLog.action)
    )
    actions = [row[0] for row in result.all()]
    return {"actions": actions}


@router.get("/operations/export")
async def export_logs(
    module: str = Query(None),
    action: str = Query(None),
    admin_user_id: int = Query(None),
    search: str = Query(""),
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """导出操作日志为CSV文件"""
    # 构建查询（与列表API相同的逻辑）
    query = select(OperationLog).options(selectinload(OperationLog.admin_user))

    if module:
        query = query.filter(OperationLog.module == module)
    if action:
        query = query.filter(OperationLog.action == action)
    if admin_user_id:
        query = query.filter(OperationLog.admin_user_id == admin_user_id)
    if search:
        query = query.filter(
            or_(
                OperationLog.description.ilike(f"%{search}%"),
                OperationLog.ip_address.ilike(f"%{search}%"),
            )
        )
    if start_date:
        start_datetime = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        query = query.filter(OperationLog.created_at >= start_datetime)
    if end_date:
        end_datetime = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        query = query.filter(OperationLog.created_at <= end_datetime)

    # 获取数据（限制最多导出10000条）
    query = query.order_by(desc(OperationLog.created_at)).limit(10000)
    result = await db.execute(query)
    logs = result.scalars().all()

    # 创建CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # 写入表头
    writer.writerow(
        [
            "ID",
            "管理员用户名",
            "管理员邮箱",
            "模块",
            "操作",
            "描述",
            "IP地址",
            "请求方法",
            "请求URL",
            "创建时间",
        ]
    )

    # 写入数据
    for log in logs:
        writer.writerow(
            [
                log.id,
                log.admin_user.username if log.admin_user else "",
                log.admin_user.email if log.admin_user else "",
                log.module,
                log.action,
                log.description,
                log.ip_address or "",
                log.request_method or "",
                log.request_url or "",
                log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            ]
        )

    # 返回CSV文件
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=operation_logs_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
        },
    )
