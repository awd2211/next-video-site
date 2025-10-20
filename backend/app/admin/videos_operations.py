"""
视频运营管理API - 批量操作和运营看板
这个文件包含视频管理的运营相关接口
"""
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import AdminUser
from app.models.video import Video, VideoStatus
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


# ==================== Schemas ====================

class BatchVideoIdsRequest(BaseModel):
    """批量操作视频ID请求"""
    ids: List[int] = Field(..., min_length=1, description="视频ID列表")


class BatchMarkRequest(BatchVideoIdsRequest):
    """批量标记请求"""
    value: bool = Field(..., description="标记值")


class BatchQualityScoreRequest(BatchVideoIdsRequest):
    """批量设置质量评分请求"""
    quality_score: int = Field(..., ge=0, le=100, description="质量评分 0-100")


class SchedulePublishRequest(BaseModel):
    """定时发布请求"""
    scheduled_publish_at: datetime = Field(..., description="定时发布时间")


class DashboardStatsResponse(BaseModel):
    """运营看板统计响应"""
    total_videos: int
    standalone_videos: int
    series_videos: int
    today_new: int
    pending_review: int
    scheduled_count: int
    trending_count: int
    pinned_count: int
    featured_count: int
    this_week_views: int


# ==================== Batch Operations ====================

@router.put("/batch/mark-trending")
async def batch_mark_trending(
    request: BatchMarkRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """批量标记/取消热门视频"""
    result = await db.execute(
        select(Video).filter(Video.id.in_(request.ids))
    )
    videos = result.scalars().all()

    if not videos:
        raise HTTPException(status_code=404, detail="未找到指定视频")

    for video in videos:
        video.is_trending = request.value

    await db.commit()

    return {
        "success": True,
        "affected": len(videos),
        "message": f"已{'标记' if request.value else '取消'}热门标记"
    }


@router.put("/batch/mark-pinned")
async def batch_mark_pinned(
    request: BatchMarkRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """批量置顶/取消置顶视频"""
    result = await db.execute(
        select(Video).filter(Video.id.in_(request.ids))
    )
    videos = result.scalars().all()

    if not videos:
        raise HTTPException(status_code=404, detail="未找到指定视频")

    for video in videos:
        video.is_pinned = request.value

    await db.commit()

    return {
        "success": True,
        "affected": len(videos),
        "message": f"已{'置顶' if request.value else '取消置顶'}"
    }


@router.put("/batch/set-quality")
async def batch_set_quality_score(
    request: BatchQualityScoreRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """批量设置质量评分"""
    result = await db.execute(
        select(Video).filter(Video.id.in_(request.ids))
    )
    videos = result.scalars().all()

    if not videos:
        raise HTTPException(status_code=404, detail="未找到指定视频")

    for video in videos:
        video.quality_score = request.quality_score

    await db.commit()

    return {
        "success": True,
        "affected": len(videos),
        "quality_score": request.quality_score,
        "message": f"已设置质量评分为 {request.quality_score}"
    }


# ==================== Scheduled Publishing ====================

@router.post("/{video_id}/schedule")
async def schedule_video_publish(
    video_id: int,
    request: SchedulePublishRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """设置视频定时发布"""
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    # Validate future time
    now = datetime.now(timezone.utc)
    if request.scheduled_publish_at <= now:
        raise HTTPException(status_code=400, detail="定时发布时间必须是未来时间")

    video.scheduled_publish_at = request.scheduled_publish_at
    # Ensure video is in DRAFT status for scheduled publishing
    if video.status != VideoStatus.DRAFT:
        video.status = VideoStatus.DRAFT

    await db.commit()

    return {
        "success": True,
        "video_id": video_id,
        "scheduled_publish_at": video.scheduled_publish_at.isoformat(),
        "message": f"已设置定时发布时间: {video.scheduled_publish_at.strftime('%Y-%m-%d %H:%M:%S')}"
    }


@router.delete("/{video_id}/schedule")
async def cancel_scheduled_publish(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """取消视频定时发布"""
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    video.scheduled_publish_at = None
    await db.commit()

    return {
        "success": True,
        "video_id": video_id,
        "message": "已取消定时发布"
    }


# ==================== Dashboard Stats ====================

@router.get("/dashboard-stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取运营看板统计数据"""
    from datetime import timedelta

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)

    # Total videos
    total_result = await db.execute(select(func.count(Video.id)))
    total_videos = total_result.scalar() or 0

    # Standalone videos (MOVIE + DOCUMENTARY)
    standalone_result = await db.execute(
        select(func.count(Video.id)).filter(
            Video.video_type.in_(['MOVIE', 'DOCUMENTARY'])
        )
    )
    standalone_videos = standalone_result.scalar() or 0

    # Series videos (TV_SERIES + ANIME)
    series_videos = total_videos - standalone_videos

    # Today new videos
    today_new_result = await db.execute(
        select(func.count(Video.id)).filter(Video.created_at >= today_start)
    )
    today_new = today_new_result.scalar() or 0

    # Pending review (DRAFT status)
    pending_result = await db.execute(
        select(func.count(Video.id)).filter(Video.status == VideoStatus.DRAFT)
    )
    pending_review = pending_result.scalar() or 0

    # Scheduled videos (future scheduled_publish_at)
    scheduled_result = await db.execute(
        select(func.count(Video.id)).filter(
            and_(
                Video.scheduled_publish_at.isnot(None),
                Video.scheduled_publish_at > now,
                Video.status == VideoStatus.DRAFT
            )
        )
    )
    scheduled_count = scheduled_result.scalar() or 0

    # Trending videos
    trending_result = await db.execute(
        select(func.count(Video.id)).filter(Video.is_trending == True)
    )
    trending_count = trending_result.scalar() or 0

    # Pinned videos
    pinned_result = await db.execute(
        select(func.count(Video.id)).filter(Video.is_pinned == True)
    )
    pinned_count = pinned_result.scalar() or 0

    # Featured videos
    featured_result = await db.execute(
        select(func.count(Video.id)).filter(Video.is_featured == True)
    )
    featured_count = featured_result.scalar() or 0

    # This week's total views
    week_views_result = await db.execute(
        select(func.sum(Video.view_count)).filter(Video.created_at >= week_start)
    )
    this_week_views = week_views_result.scalar() or 0

    return DashboardStatsResponse(
        total_videos=total_videos,
        standalone_videos=standalone_videos,
        series_videos=series_videos,
        today_new=today_new,
        pending_review=pending_review,
        scheduled_count=scheduled_count,
        trending_count=trending_count,
        pinned_count=pinned_count,
        featured_count=featured_count,
        this_week_views=this_week_views,
    )


# ==================== Quick Toggle Operations ====================

@router.put("/{video_id}/toggle-trending")
async def toggle_video_trending(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """快速切换视频热门状态"""
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    video.is_trending = not video.is_trending
    await db.commit()

    return {
        "success": True,
        "video_id": video_id,
        "is_trending": video.is_trending
    }


@router.put("/{video_id}/toggle-pinned")
async def toggle_video_pinned(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """快速切换视频置顶状态"""
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    video.is_pinned = not video.is_pinned
    await db.commit()

    return {
        "success": True,
        "video_id": video_id,
        "is_pinned": video.is_pinned
    }
