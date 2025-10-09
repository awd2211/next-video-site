from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional
from app.database import get_db
from app.models.video import Video, VideoStatus
from app.schemas.video import VideoListResponse, VideoDetailResponse, PaginatedResponse
from app.config import settings

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    video_type: Optional[str] = None,
    country_id: Optional[int] = None,
    category_id: Optional[int] = None,
    year: Optional[int] = None,
    sort_by: str = Query("created_at", regex="^(created_at|view_count|average_rating)$"),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated list of published videos"""
    query = select(Video).filter(Video.status == VideoStatus.PUBLISHED)

    # Filters
    if video_type:
        query = query.filter(Video.video_type == video_type)
    if country_id:
        query = query.filter(Video.country_id == country_id)
    if year:
        query = query.filter(Video.release_year == year)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar()

    # Sort
    if sort_by == "view_count":
        query = query.order_by(desc(Video.view_count))
    elif sort_by == "average_rating":
        query = query.order_by(desc(Video.average_rating))
    else:
        query = query.order_by(desc(Video.created_at))

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    videos = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": videos,
    }


@router.get("/{video_id}", response_model=VideoDetailResponse)
async def get_video(
    video_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get video details"""
    result = await db.execute(
        select(Video).filter(Video.id == video_id, Video.status == VideoStatus.PUBLISHED)
    )
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Increment view count (should be done asynchronously in production)
    video.view_count += 1
    await db.commit()

    return video


@router.get("/trending", response_model=PaginatedResponse)
async def get_trending_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get trending videos (most viewed in last 7 days)"""
    # Simplified version - in production, use a more sophisticated trending algorithm
    query = select(Video).filter(Video.status == VideoStatus.PUBLISHED).order_by(desc(Video.view_count))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar()

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    videos = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": videos,
    }
