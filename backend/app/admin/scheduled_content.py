"""
内容调度系统 - 定时发布功能
支持视频、公告、横幅等内容的定时发布
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.content import Announcement, Banner
from app.models.user import AdminUser
from app.models.video import Video, VideoStatus
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


# ========== Schemas ==========


class VideoScheduleCreate(BaseModel):
    video_id: int
    scheduled_publish_at: datetime
    auto_publish: bool = True
    notify_subscribers: bool = False


class VideoScheduleUpdate(BaseModel):
    scheduled_publish_at: Optional[datetime] = None
    auto_publish: Optional[bool] = None
    notify_subscribers: Optional[bool] = None


class AnnouncementScheduleCreate(BaseModel):
    announcement_id: int
    scheduled_publish_at: datetime
    scheduled_expire_at: Optional[datetime] = None
    auto_publish: bool = True


class BannerScheduleCreate(BaseModel):
    banner_id: int
    scheduled_start_at: datetime
    scheduled_end_at: Optional[datetime] = None
    auto_activate: bool = True


# ========== Video Scheduled Publishing ==========


@router.get("/videos/scheduled")
async def get_scheduled_videos(
    status: Optional[str] = Query(None, regex="^(pending|published|cancelled)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取所有定时发布的视频
    """
    now = datetime.now(timezone.utc)

    # 构建查询条件
    conditions = [Video.scheduled_publish_at.isnot(None)]

    if status == "pending":
        # 待发布：定时时间未到且状态为draft
        conditions.extend([Video.scheduled_publish_at > now, Video.status == VideoStatus.DRAFT])
    elif status == "published":
        # 已发布：定时时间已过且状态为published
        conditions.extend(
            [Video.scheduled_publish_at <= now, Video.status == VideoStatus.PUBLISHED]
        )
    elif status == "cancelled":
        # 已取消：有定时时间但已删除或拒绝
        conditions.append(
            or_(Video.status == VideoStatus.DELETED, Video.status == VideoStatus.REJECTED)
        )

    query = select(Video).where(and_(*conditions)).order_by(Video.scheduled_publish_at)

    # 分页
    result = await db.execute(query.offset(skip).limit(limit))
    videos = result.scalars().all()

    # 统计总数
    count_query = select(Video).where(and_(*conditions))
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())

    return {
        "items": [
            {
                "id": v.id,
                "title": v.title,
                "status": v.status.value if v.status else None,
                "scheduled_publish_at": v.scheduled_publish_at,
                "created_at": v.created_at,
                "updated_at": v.updated_at,
            }
            for v in videos
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("/videos/schedule")
async def schedule_video_publishing(
    schedule_data: VideoScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    为视频设置定时发布
    """
    # 获取视频
    result = await db.execute(select(Video).where(Video.id == schedule_data.video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # 检查视频状态（只能为draft状态的视频设置定时发布）
    if video.status != VideoStatus.DRAFT:
        raise HTTPException(
            status_code=400, detail="Only draft videos can be scheduled for publishing"
        )

    # 检查定时时间必须是未来时间
    if schedule_data.scheduled_publish_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Scheduled time must be in the future")

    # 设置定时发布
    video.scheduled_publish_at = schedule_data.scheduled_publish_at

    await db.commit()
    await db.refresh(video)

    logger.info(
        f"管理员 {current_admin.username} 为视频 {video.id} 设置定时发布: {schedule_data.scheduled_publish_at}"
    )

    return {
        "id": video.id,
        "title": video.title,
        "scheduled_publish_at": video.scheduled_publish_at,
        "status": video.status.value if video.status else None,
    }


@router.put("/videos/{video_id}/schedule")
async def update_video_schedule(
    video_id: int,
    schedule_data: VideoScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    更新视频的定时发布时间
    """
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if video.scheduled_publish_at is None:
        raise HTTPException(status_code=400, detail="Video has no scheduled publishing time")

    # 更新定时发布时间
    if schedule_data.scheduled_publish_at:
        if schedule_data.scheduled_publish_at <= datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Scheduled time must be in the future")
        video.scheduled_publish_at = schedule_data.scheduled_publish_at

    await db.commit()
    await db.refresh(video)

    logger.info(f"管理员 {current_admin.username} 更新了视频 {video_id} 的定时发布时间")

    return {
        "id": video.id,
        "title": video.title,
        "scheduled_publish_at": video.scheduled_publish_at,
        "status": video.status.value if video.status else None,
    }


@router.delete("/videos/{video_id}/schedule")
async def cancel_video_schedule(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    取消视频的定时发布
    """
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if video.scheduled_publish_at is None:
        raise HTTPException(status_code=400, detail="Video has no scheduled publishing time")

    # 取消定时发布
    video.scheduled_publish_at = None

    await db.commit()

    logger.info(f"管理员 {current_admin.username} 取消了视频 {video_id} 的定时发布")

    return {"message": "Scheduled publishing cancelled"}


@router.post("/videos/publish-scheduled")
async def publish_scheduled_videos(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    手动触发发布所有到期的定时视频（通常由定时任务调用）
    """
    now = datetime.now(timezone.utc)

    # 查找所有到期的定时视频
    result = await db.execute(
        select(Video).where(
            and_(
                Video.scheduled_publish_at.isnot(None),
                Video.scheduled_publish_at <= now,
                Video.status == VideoStatus.DRAFT,
            )
        )
    )
    videos = result.scalars().all()

    published_count = 0
    for video in videos:
        # 发布视频
        video.status = VideoStatus.PUBLISHED
        video.published_at = now
        # 清除定时发布时间
        video.scheduled_publish_at = None
        published_count += 1

    await db.commit()

    logger.info(
        f"管理员 {current_admin.username} 手动触发定时发布，共发布 {published_count} 个视频"
    )

    return {"message": f"Published {published_count} scheduled videos", "count": published_count}


# ========== Statistics ==========


@router.get("/stats")
async def get_scheduling_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取内容调度统计信息
    """
    now = datetime.now(timezone.utc)

    # 待发布的视频数量
    pending_videos_result = await db.execute(
        select(Video).where(
            and_(
                Video.scheduled_publish_at.isnot(None),
                Video.scheduled_publish_at > now,
                Video.status == VideoStatus.DRAFT,
            )
        )
    )
    pending_videos = len(pending_videos_result.scalars().all())

    # 今天到期的视频数量
    from datetime import timedelta

    today_end = datetime.now(timezone.utc).replace(
        hour=23, minute=59, second=59, microsecond=999999
    )
    today_videos_result = await db.execute(
        select(Video).where(
            and_(
                Video.scheduled_publish_at.isnot(None),
                Video.scheduled_publish_at > now,
                Video.scheduled_publish_at <= today_end,
                Video.status == VideoStatus.DRAFT,
            )
        )
    )
    today_videos = len(today_videos_result.scalars().all())

    # 过期未发布的视频（定时时间已过但仍为draft状态）
    overdue_videos_result = await db.execute(
        select(Video).where(
            and_(
                Video.scheduled_publish_at.isnot(None),
                Video.scheduled_publish_at <= now,
                Video.status == VideoStatus.DRAFT,
            )
        )
    )
    overdue_videos = len(overdue_videos_result.scalars().all())

    return {
        "pending_scheduled": pending_videos,
        "scheduled_today": today_videos,
        "overdue": overdue_videos,
        "total_scheduled": pending_videos + overdue_videos,
    }
