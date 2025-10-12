from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.content import Announcement
from app.models.user import AdminUser
from app.schemas.admin_content import (
    AnnouncementCreate,
    AnnouncementResponse,
    AnnouncementUpdate,
    PaginatedAnnouncementResponse,
)
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


@router.get("/announcements", response_model=dict)
async def get_announcements(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取公告列表"""
    query = select(Announcement).order_by(
        desc(Announcement.is_pinned), desc(Announcement.created_at)
    )

    if is_active is not None:
        query = query.where(Announcement.is_active == is_active)

    if type:
        query = query.where(Announcement.type == type)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar() or 0

    # Pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    announcements = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [AnnouncementResponse.model_validate(a) for a in announcements],
    }


@router.get("/announcements/{announcement_id}", response_model=AnnouncementResponse)
async def get_announcement(
    announcement_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取单个公告详情"""
    result = await db.execute(
        select(Announcement).where(Announcement.id == announcement_id)
    )
    announcement = result.scalar_one_or_none()

    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")

    return AnnouncementResponse.model_validate(announcement)


@router.post("/announcements", response_model=AnnouncementResponse)
async def create_announcement(
    data: AnnouncementCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """创建公告"""
    announcement = Announcement(
        title=data.title,
        content=data.content,
        type=data.type,
        is_active=data.is_active,
        is_pinned=data.is_pinned,
        start_date=data.start_date,
        end_date=data.end_date,
    )

    db.add(announcement)
    await db.commit()
    await db.refresh(announcement)

    return AnnouncementResponse.model_validate(announcement)


@router.put("/announcements/{announcement_id}", response_model=AnnouncementResponse)
async def update_announcement(
    announcement_id: int,
    data: AnnouncementUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """更新公告"""
    result = await db.execute(
        select(Announcement).where(Announcement.id == announcement_id)
    )
    announcement = result.scalar_one_or_none()

    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(announcement, field, value)

    await db.commit()
    await db.refresh(announcement)

    return AnnouncementResponse.model_validate(announcement)


@router.delete("/announcements/{announcement_id}")
async def delete_announcement(
    announcement_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """删除公告"""
    result = await db.execute(
        select(Announcement).where(Announcement.id == announcement_id)
    )
    announcement = result.scalar_one_or_none()

    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")

    await db.delete(announcement)
    await db.commit()

    return {"message": "公告已删除"}


@router.patch("/announcements/{announcement_id}/toggle-active")
async def toggle_announcement_active(
    announcement_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """切换公告激活状态"""
    result = await db.execute(
        select(Announcement).where(Announcement.id == announcement_id)
    )
    announcement = result.scalar_one_or_none()

    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")

    announcement.is_active = not announcement.is_active
    await db.commit()

    return {"message": "状态已更新", "is_active": announcement.is_active}


@router.patch("/announcements/{announcement_id}/toggle-pinned")
async def toggle_announcement_pinned(
    announcement_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """切换公告置顶状态"""
    result = await db.execute(
        select(Announcement).where(Announcement.id == announcement_id)
    )
    announcement = result.scalar_one_or_none()

    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")

    announcement.is_pinned = not announcement.is_pinned
    await db.commit()

    return {"message": "置顶状态已更新", "is_pinned": announcement.is_pinned}
