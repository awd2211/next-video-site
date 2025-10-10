"""
转码状态查询 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.video import Video
from app.models.user import AdminUser
from app.utils.dependencies import get_current_admin_user
from typing import Optional
from pydantic import BaseModel

router = APIRouter()


class TranscodeStatusResponse(BaseModel):
    """转码状态响应"""
    video_id: int
    status: Optional[str] = None  # pending, processing, completed, failed
    progress: int = 0  # 0-100
    error: Optional[str] = None
    h264_transcode_at: Optional[str] = None
    av1_transcode_at: Optional[str] = None
    is_av1_available: bool = False

    class Config:
        from_attributes = True


@router.get("/videos/{video_id}/transcode-status", response_model=TranscodeStatusResponse)
async def get_transcode_status(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取视频转码状态

    用于管理后台轮询转码进度
    """
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    return TranscodeStatusResponse(
        video_id=video.id,
        status=video.transcode_status,
        progress=video.transcode_progress or 0,
        error=video.transcode_error,
        h264_transcode_at=video.h264_transcode_at.isoformat() if video.h264_transcode_at else None,
        av1_transcode_at=video.av1_transcode_at.isoformat() if video.av1_transcode_at else None,
        is_av1_available=video.is_av1_available or False,
    )


@router.post("/videos/{video_id}/retry-transcode")
async def retry_transcode(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    重试失败的转码任务

    适用于status=failed的视频
    """
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if not video.video_url:
        raise HTTPException(status_code=400, detail="Video has no source URL")

    # 触发转码任务
    from app.tasks.transcode_av1 import transcode_video_dual_format
    task = transcode_video_dual_format.delay(video_id)

    # 重置状态
    video.transcode_status = 'pending'
    video.transcode_progress = 0
    video.transcode_error = None
    await db.commit()

    return {
        "message": "Transcode task triggered",
        "video_id": video_id,
        "task_id": task.id,
        "status": "pending"
    }
