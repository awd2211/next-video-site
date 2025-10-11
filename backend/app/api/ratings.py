from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.comment import Rating
from app.models.user import User
from app.models.video import Video
from app.schemas.rating import (
    RatingCreate,
    RatingResponse,
    VideoRatingStats,
)
from app.utils.dependencies import get_current_active_user, get_current_user
from app.utils.rate_limit import RateLimitPresets, limiter

router = APIRouter()


@router.post("/", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimitPresets.COMMENT)  # 评分限流: 30/分钟 (与评论相同)
async def create_or_update_rating(
    request: Request,
    rating_data: RatingCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Rate a video. If user has already rated this video, update the rating.
    """
    # Verify video exists
    video_result = await db.execute(
        select(Video).where(Video.id == rating_data.video_id)
    )
    video = video_result.scalar_one_or_none()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
        )

    # Check if user already rated this video
    existing_rating_result = await db.execute(
        select(Rating).where(
            and_(
                Rating.video_id == rating_data.video_id,
                Rating.user_id == current_user.id,
            )
        )
    )
    existing_rating = existing_rating_result.scalar_one_or_none()

    if existing_rating:
        # Update existing rating
        existing_rating.score
        existing_rating.score = rating_data.score
        rating = existing_rating
    else:
        # Create new rating
        rating = Rating(
            video_id=rating_data.video_id,
            user_id=current_user.id,
            score=rating_data.score,
        )
        db.add(rating)

    await db.commit()
    await db.refresh(rating)

    # 注意：评分统计由数据库触发器自动更新，无需手动计算
    # 这样可以避免并发竞态条件

    return RatingResponse.model_validate(rating)


@router.get("/video/{video_id}/stats", response_model=VideoRatingStats)
async def get_video_rating_stats(
    video_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get rating statistics for a video"""
    # Verify video exists
    video_result = await db.execute(select(Video).where(Video.id == video_id))
    video = video_result.scalar_one_or_none()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
        )

    # Get user's rating if logged in
    user_rating = None
    if current_user:
        user_rating_result = await db.execute(
            select(Rating.score).where(
                and_(Rating.video_id == video_id, Rating.user_id == current_user.id)
            )
        )
        user_rating_row = user_rating_result.scalar_one_or_none()
        if user_rating_row:
            user_rating = float(user_rating_row)

    return VideoRatingStats(
        video_id=video_id,
        average_rating=video.average_rating,
        rating_count=video.rating_count,
        user_rating=user_rating,
    )


@router.get("/video/{video_id}/my-rating", response_model=Optional[RatingResponse])
async def get_my_rating(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's rating for a video"""
    result = await db.execute(
        select(Rating).where(
            and_(Rating.video_id == video_id, Rating.user_id == current_user.id)
        )
    )
    rating = result.scalar_one_or_none()

    if not rating:
        return None

    return RatingResponse.model_validate(rating)


@router.delete("/video/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rating(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete user's rating for a video"""
    result = await db.execute(
        select(Rating).where(
            and_(Rating.video_id == video_id, Rating.user_id == current_user.id)
        )
    )
    rating = result.scalar_one_or_none()

    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found"
        )

    await db.delete(rating)
    await db.commit()

    # Recalculate video average rating
    video_result = await db.execute(select(Video).where(Video.id == video_id))
    video = video_result.scalar_one_or_none()

    if video:
        stats_result = await db.execute(
            select(
                func.avg(Rating.score).label("avg_score"),
                func.count(Rating.id).label("count"),
            ).where(Rating.video_id == video_id)
        )
        stats = stats_result.one()

        video.average_rating = float(stats.avg_score) if stats.avg_score else 0.0
        video.rating_count = stats.count

        await db.commit()

    return None
