"""
Admin Notifications API
管理员通知API端点
"""

import math
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, delete, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.notification import AdminNotification
from app.models.user import AdminUser
from app.utils.dependencies import get_current_admin_user
from app.utils.admin_notification_service import AdminNotificationService

router = APIRouter()


# Schemas
class AdminNotificationResponse(BaseModel):
    """管理员通知响应模型"""

    id: int
    admin_user_id: Optional[int]
    type: str
    title: str
    content: str
    severity: str
    related_type: Optional[str]
    related_id: Optional[int]
    link: Optional[str]
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime]

    class Config:
        from_attributes = True


class AdminNotificationListResponse(BaseModel):
    """管理员通知列表响应"""

    notifications: list[AdminNotificationResponse]
    total: int
    page: int
    page_size: int
    pages: int
    unread_count: int


class AdminNotificationStatsResponse(BaseModel):
    """管理员通知统计响应"""

    total: int
    unread: int
    read: int
    by_severity: dict


@router.get("", response_model=AdminNotificationListResponse)
async def get_admin_notifications(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    type: Optional[str] = Query(None, description="通知类型筛选"),
    severity: Optional[str] = Query(None, description="严重程度筛选"),
    is_read: Optional[bool] = Query(None, description="已读状态筛选"),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取当前管理员的通知列表

    - **page**: 页码 (从1开始)
    - **page_size**: 每页数量 (1-100)
    - **type**: 通知类型筛选 (可选)
    - **severity**: 严重程度筛选 (info/warning/error/critical)
    - **is_read**: 已读状态筛选 (可选)
    """
    # 构建查询条件: 广播给所有管理员 或 指定给当前管理员
    conditions = [
        or_(
            AdminNotification.admin_user_id.is_(None),
            AdminNotification.admin_user_id == current_admin.id,
        )
    ]

    if type:
        conditions.append(AdminNotification.type == type)

    if severity:
        conditions.append(AdminNotification.severity == severity)

    if is_read is not None:
        conditions.append(AdminNotification.is_read == is_read)

    # 查询总数
    count_query = select(func.count(AdminNotification.id)).where(and_(*conditions))
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 查询未读数量
    unread_count = await AdminNotificationService.get_unread_count(db, current_admin.id)

    # 分页查询通知
    offset = (page - 1) * page_size
    query = (
        select(AdminNotification)
        .where(and_(*conditions))
        .order_by(desc(AdminNotification.created_at))
        .offset(offset)
        .limit(page_size)
    )

    result = await db.execute(query)
    notifications = result.scalars().all()

    return AdminNotificationListResponse(
        notifications=[AdminNotificationResponse.model_validate(n) for n in notifications],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if page_size > 0 and total > 0 else 0,
        unread_count=unread_count,
    )


@router.get("/stats", response_model=AdminNotificationStatsResponse)
async def get_admin_notification_stats(
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取当前管理员的通知统计

    返回总通知数、未读数、已读数、按严重程度统计
    """
    # 基础条件
    base_conditions = or_(
        AdminNotification.admin_user_id.is_(None),
        AdminNotification.admin_user_id == current_admin.id,
    )

    # 总通知数
    total_query = select(func.count(AdminNotification.id)).where(base_conditions)
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0

    # 未读数
    unread_count = await AdminNotificationService.get_unread_count(db, current_admin.id)

    # 按严重程度统计
    severity_query = (
        select(AdminNotification.severity, func.count(AdminNotification.id))
        .where(and_(base_conditions, AdminNotification.is_read.is_(False)))
        .group_by(AdminNotification.severity)
    )
    severity_result = await db.execute(severity_query)
    by_severity = {row[0]: row[1] for row in severity_result.all()}

    return AdminNotificationStatsResponse(
        total=total,
        unread=unread_count,
        read=total - unread_count,
        by_severity=by_severity,
    )


@router.patch("/{notification_id}", response_model=AdminNotificationResponse)
async def mark_admin_notification_as_read(
    notification_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    标记指定通知为已读

    - **notification_id**: 通知ID
    """
    success = await AdminNotificationService.mark_as_read(
        db=db,
        notification_id=notification_id,
        admin_user_id=current_admin.id,
    )

    if not success:
        raise HTTPException(status_code=404, detail="通知不存在或无权访问")

    # 重新查询通知
    query = select(AdminNotification).where(AdminNotification.id == notification_id)
    result = await db.execute(query)
    notification = result.scalar_one_or_none()

    return AdminNotificationResponse.model_validate(notification)


@router.post("/mark-all-read")
async def mark_all_admin_notifications_as_read(
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    标记所有通知为已读
    """
    # 查询所有未读通知
    query = select(AdminNotification).where(
        and_(
            or_(
                AdminNotification.admin_user_id.is_(None),
                AdminNotification.admin_user_id == current_admin.id,
            ),
            AdminNotification.is_read.is_(False),
        )
    )
    result = await db.execute(query)
    notifications = result.scalars().all()

    # 批量更新
    count = 0
    for notification in notifications:
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        count += 1

    await db.commit()

    return {"message": f"已标记 {count} 条通知为已读", "count": count}


@router.delete("/{notification_id}")
async def delete_admin_notification(
    notification_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除指定通知

    - **notification_id**: 通知ID
    """
    # 查询通知
    query = select(AdminNotification).where(
        and_(
            AdminNotification.id == notification_id,
            or_(
                AdminNotification.admin_user_id.is_(None),
                AdminNotification.admin_user_id == current_admin.id,
            ),
        )
    )
    result = await db.execute(query)
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在或无权访问")

    # 删除通知
    await db.delete(notification)
    await db.commit()

    return {"message": "通知已删除"}


@router.post("/clear-all")
async def clear_all_admin_notifications(
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    清空所有通知
    """
    # 删除所有通知（广播或指定给当前管理员的）
    query = delete(AdminNotification).where(
        or_(
            AdminNotification.admin_user_id.is_(None),
            AdminNotification.admin_user_id == current_admin.id,
        )
    )
    result = await db.execute(query)
    await db.commit()

    count = result.rowcount

    return {"message": f"已清空 {count} 条通知", "count": count}


@router.post("/test-notification")
async def create_test_notification(
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    创建测试通知 (用于开发测试)
    """
    await AdminNotificationService.create_admin_notification(
        db=db,
        admin_user_id=current_admin.id,
        type="system_message",
        title="测试通知",
        content="这是一条测试通知消息，用于验证通知系统是否正常工作。",
        severity="info",
        link="/",
    )

    return {"message": "测试通知已创建"}
