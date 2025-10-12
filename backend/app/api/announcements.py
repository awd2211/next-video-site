from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.content import Announcement
from app.schemas.content import AnnouncementResponse

router = APIRouter()


@router.get("/", response_model=List[AnnouncementResponse])
async def get_active_announcements(
    type: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    获取激活的公告列表（用户端）
    - 只返回激活的公告
    - 只返回在有效期内的公告
    - 置顶公告排在前面
    """
    now = datetime.utcnow()

    query = select(Announcement).where(
        and_(
            Announcement.is_active == True,
            or_(
                Announcement.start_date == None,
                Announcement.start_date <= now,
            ),
            or_(
                Announcement.end_date == None,
                Announcement.end_date >= now,
            ),
        )
    )

    if type:
        query = query.where(Announcement.type == type)

    query = query.order_by(
        desc(Announcement.is_pinned),
        desc(Announcement.created_at)
    ).limit(limit)

    result = await db.execute(query)
    announcements = result.scalars().all()

    return [AnnouncementResponse.model_validate(a) for a in announcements]


@router.get("/{announcement_id}", response_model=AnnouncementResponse)
async def get_announcement_detail(
    announcement_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取单个公告详情（用户端）"""
    result = await db.execute(
        select(Announcement).where(
            and_(
                Announcement.id == announcement_id,
                Announcement.is_active == True,
            )
        )
    )
    announcement = result.scalar_one_or_none()

    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在或已关闭")

    return AnnouncementResponse.model_validate(announcement)
