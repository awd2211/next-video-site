from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import (
    NotificationListResponse,
    NotificationResponse,
    NotificationStatsResponse,
    NotificationUpdate,
)
from app.utils.dependencies import get_current_active_user

router = APIRouter()


@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    type: Optional[str] = Query(None, description="通知类型筛选"),
    is_read: Optional[bool] = Query(None, description="已读状态筛选"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取当前用户的通知列表

    - **page**: 页码 (从1开始)
    - **page_size**: 每页数量 (1-100)
    - **type**: 通知类型筛选 (可选)
    - **is_read**: 已读状态筛选 (可选)
    """
    # 构建查询条件
    conditions = [Notification.user_id == current_user.id]

    if type:
        conditions.append(Notification.type == type)

    if is_read is not None:
        conditions.append(Notification.is_read == is_read)

    # 查询总数
    count_query = select(func.count(Notification.id)).where(and_(*conditions))
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 查询未读数量
    unread_query = select(func.count(Notification.id)).where(
        and_(Notification.user_id == current_user.id, Notification.is_read == False)
    )
    unread_result = await db.execute(unread_query)
    unread_count = unread_result.scalar()

    # 分页查询通知
    offset = (page - 1) * page_size
    query = (
        select(Notification)
        .where(and_(*conditions))
        .order_by(Notification.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )

    result = await db.execute(query)
    notifications = result.scalars().all()

    return NotificationListResponse(
        notifications=[NotificationResponse.model_validate(n) for n in notifications],
        total=total,
        page=page,
        page_size=page_size,
        unread_count=unread_count,
    )


@router.get("/stats", response_model=NotificationStatsResponse)
async def get_notification_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取当前用户的通知统计

    返回总通知数、未读数、已读数
    """
    # 总通知数
    total_query = select(func.count(Notification.id)).where(
        Notification.user_id == current_user.id
    )
    total_result = await db.execute(total_query)
    total = total_result.scalar()

    # 未读数
    unread_query = select(func.count(Notification.id)).where(
        and_(Notification.user_id == current_user.id, Notification.is_read == False)
    )
    unread_result = await db.execute(unread_query)
    unread = unread_result.scalar()

    return NotificationStatsResponse(
        total=total,
        unread=unread,
        read=total - unread,
    )


@router.patch("/{notification_id}", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    标记指定通知为已读

    - **notification_id**: 通知ID
    """
    # 查询通知
    query = select(Notification).where(
        and_(
            Notification.id == notification_id, Notification.user_id == current_user.id
        )
    )
    result = await db.execute(query)
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")

    # 更新为已读
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(notification)

    return NotificationResponse.model_validate(notification)


@router.post("/mark-all-read")
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    标记所有通知为已读
    """
    # 查询所有未读通知
    query = select(Notification).where(
        and_(Notification.user_id == current_user.id, Notification.is_read == False)
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
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除指定通知

    - **notification_id**: 通知ID
    """
    # 查询通知
    query = select(Notification).where(
        and_(
            Notification.id == notification_id, Notification.user_id == current_user.id
        )
    )
    result = await db.execute(query)
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")

    # 删除通知
    await db.delete(notification)
    await db.commit()

    return {"message": "通知已删除"}


@router.post("/clear-all")
async def clear_all_notifications(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    清空所有通知
    """
    # 删除所有通知
    query = delete(Notification).where(Notification.user_id == current_user.id)
    result = await db.execute(query)
    await db.commit()

    count = result.rowcount

    return {"message": f"已清空 {count} 条通知", "count": count}
