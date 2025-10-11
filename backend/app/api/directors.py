from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.video import Director, Video, VideoDirector
from app.schemas.person import (
    DirectorDetailResponse,
    DirectorResponse,
    PaginatedDirectorResponse,
)
from app.utils.cache import Cache

router = APIRouter()


@router.get("/", response_model=PaginatedDirectorResponse)
async def get_directors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", description="Search directors by name"),
    db: AsyncSession = Depends(get_db),
):
    """Get list of directors with pagination and search (cached for 15 minutes)"""
    # 生成缓存键
    cache_key = f"directors_list:{page}:{page_size}:{search or 'all'}"

    # 尝试从缓存获取
    cached = await Cache.get(cache_key)
    if cached is not None:
        return cached

    # Build query
    query = select(Director)

    # Apply search filter
    if search:
        query = query.where(Director.name.ilike(f"%{search}%"))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = (
        query.order_by(Director.name).offset((page - 1) * page_size).limit(page_size)
    )

    result = await db.execute(query)
    directors = result.scalars().all()

    items = [DirectorResponse.model_validate(director) for director in directors]

    response = PaginatedDirectorResponse(
        total=total, page=page, page_size=page_size, items=items
    )

    # 缓存15分钟
    await Cache.set(cache_key, response, ttl=900)

    return response


@router.get("/{director_id}", response_model=DirectorDetailResponse)
async def get_director(
    director_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get director details with their videos"""
    query = (
        select(Director)
        .where(Director.id == director_id)
        .options(
            selectinload(Director.video_directors).selectinload(VideoDirector.video)
        )
    )

    result = await db.execute(query)
    director = result.scalar_one_or_none()

    if not director:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Director not found"
        )

    # Get videos directed by this director
    videos = [vd.video for vd in director.video_directors if vd.video]

    # Build response
    director_data = DirectorDetailResponse.model_validate(director)
    director_data.videos = videos

    return director_data


@router.get("/{director_id}/videos", response_model=dict)
async def get_director_videos(
    director_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get videos directed by a specific director"""
    # Verify director exists
    director_result = await db.execute(
        select(Director).where(Director.id == director_id)
    )
    director = director_result.scalar_one_or_none()
    if not director:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Director not found"
        )

    # Count total videos
    count_query = (
        select(func.count())
        .select_from(VideoDirector)
        .where(VideoDirector.director_id == director_id)
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated videos
    query = (
        select(Video)
        .join(VideoDirector, VideoDirector.video_id == Video.id)
        .where(VideoDirector.director_id == director_id)
        .order_by(Video.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    videos = result.scalars().all()

    from app.schemas.video import VideoListResponse

    items = [VideoListResponse.model_validate(video) for video in videos]

    return {"total": total, "page": page, "page_size": page_size, "items": items}
