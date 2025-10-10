"""
分享相关 API 端点
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.share import VideoShare, SharePlatform
from app.schemas.share import ShareCreate, ShareResponse, ShareStatsResponse
from app.utils.dependencies import get_current_user, get_current_user_optional

router = APIRouter()


@router.post("/", response_model=ShareResponse, summary="记录分享")
async def create_share(
    share_data: ShareCreate,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    记录视频分享行为

    - **video_id**: 被分享的视频ID
    - **platform**: 分享平台 (wechat, weibo, qq, qzone, twitter, facebook, link, other)

    未登录用户也可以分享,但不会记录user_id
    """
    # 创建分享记录
    share = VideoShare(
        video_id=share_data.video_id,
        user_id=current_user.id if current_user else None,
        platform=share_data.platform,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:500],
    )

    db.add(share)
    await db.commit()
    await db.refresh(share)

    return share


@router.get("/video/{video_id}/stats", response_model=ShareStatsResponse, summary="获取视频分享统计")
async def get_video_share_stats(
    video_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    获取指定视频的分享统计数据

    包括:
    - 总分享次数
    - 各平台分享统计
    - 最近7天分享次数
    """
    # 总分享次数
    total_result = await db.execute(
        select(func.count(VideoShare.id)).where(VideoShare.video_id == video_id)
    )
    total_shares = total_result.scalar() or 0

    # 各平台统计
    platform_result = await db.execute(
        select(
            VideoShare.platform,
            func.count(VideoShare.id).label("count")
        )
        .where(VideoShare.video_id == video_id)
        .group_by(VideoShare.platform)
    )
    platform_stats = {
        str(row.platform): row.count
        for row in platform_result.all()
    }

    # 最近7天分享次数
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_result = await db.execute(
        select(func.count(VideoShare.id)).where(
            and_(
                VideoShare.video_id == video_id,
                VideoShare.shared_at >= seven_days_ago
            )
        )
    )
    recent_shares = recent_result.scalar() or 0

    return ShareStatsResponse(
        total_shares=total_shares,
        platform_stats=platform_stats,
        recent_shares=recent_shares,
    )


@router.get("/my-shares", response_model=list[ShareResponse], summary="获取我的分享记录")
async def get_my_shares(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取当前用户的分享记录

    需要登录
    """
    result = await db.execute(
        select(VideoShare)
        .where(VideoShare.user_id == current_user.id)
        .order_by(VideoShare.shared_at.desc())
        .offset(skip)
        .limit(limit)
    )
    shares = result.scalars().all()

    return shares
