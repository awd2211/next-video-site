import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import timedelta
from app.database import get_db
from app.models.video import Video, VideoStatus
from app.models.user import User
from app.schemas.video import VideoListResponse, VideoDetailResponse, PaginatedResponse
from app.config import settings
from app.utils.cache import Cache
from app.utils.dependencies import get_current_user
from app.utils.minio_client import minio_client

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
        "pages": math.ceil(total / page_size) if page_size > 0 else 0,
        "items": videos,
    }


@router.get("/trending", response_model=PaginatedResponse)
async def get_trending_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get trending videos (cached for 10 minutes)"""
    # 生成缓存键
    cache_key = f"trending_videos:page_{page}:size_{page_size}"

    # 尝试从缓存获取
    cached = await Cache.get(cache_key)
    if cached is not None:
        return cached

    # 从数据库查询
    query = select(Video).options(
        selectinload(Video.country)
    ).filter(Video.status == VideoStatus.PUBLISHED).order_by(desc(Video.view_count))

    # Count total
    count_query = select(func.count()).select_from(
        select(Video).filter(Video.status == VideoStatus.PUBLISHED).subquery()
    )
    result = await db.execute(count_query)
    total = result.scalar()

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    videos = result.scalars().all()

    response = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size) if page_size > 0 else 0,
        "items": [VideoListResponse.model_validate(v) for v in videos],
    }

    # 缓存10分钟
    await Cache.set(cache_key, response, ttl=600)

    return response


@router.get("/featured", response_model=PaginatedResponse)
async def get_featured_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get featured videos (cached for 15 minutes)"""
    # 生成缓存键
    cache_key = f"featured_videos:page_{page}:size_{page_size}"

    # 尝试从缓存获取
    cached = await Cache.get(cache_key)
    if cached is not None:
        return cached

    # 从数据库查询
    query = select(Video).options(
        selectinload(Video.country)
    ).filter(
        Video.status == VideoStatus.PUBLISHED,
        Video.is_featured == True
    ).order_by(desc(Video.sort_order), desc(Video.created_at))

    # Count total
    count_query = select(func.count()).select_from(
        select(Video).filter(
            Video.status == VideoStatus.PUBLISHED,
            Video.is_featured == True
        ).subquery()
    )
    result = await db.execute(count_query)
    total = result.scalar()

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    videos = result.scalars().all()

    response = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size) if page_size > 0 else 0,
        "items": [VideoListResponse.model_validate(v) for v in videos],
    }

    # 缓存15分钟
    await Cache.set(cache_key, response, ttl=900)

    return response


@router.get("/recommended", response_model=PaginatedResponse)
async def get_recommended_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get recommended videos (cached for 15 minutes)"""
    # 生成缓存键
    cache_key = f"recommended_videos:page_{page}:size_{page_size}"

    # 尝试从缓存获取
    cached = await Cache.get(cache_key)
    if cached is not None:
        return cached

    # 从数据库查询
    query = select(Video).options(
        selectinload(Video.country)
    ).filter(
        Video.status == VideoStatus.PUBLISHED,
        Video.is_recommended == True
    ).order_by(desc(Video.sort_order), desc(Video.created_at))

    # Count total
    count_query = select(func.count()).select_from(
        select(Video).filter(
            Video.status == VideoStatus.PUBLISHED,
            Video.is_recommended == True
        ).subquery()
    )
    result = await db.execute(count_query)
    total = result.scalar()

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    videos = result.scalars().all()

    response = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size) if page_size > 0 else 0,
        "items": [VideoListResponse.model_validate(v) for v in videos],
    }

    # 缓存15分钟
    await Cache.set(cache_key, response, ttl=900)

    return response


@router.get("/{video_id}", response_model=VideoDetailResponse)
async def get_video(
    video_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get video details with eagerly loaded relationships"""
    # 使用selectinload预加载所有关联数据，避免N+1查询问题
    result = await db.execute(
        select(Video)
        .options(
            selectinload(Video.country),
            selectinload(Video.video_categories),
            selectinload(Video.video_tags),
            selectinload(Video.video_actors),
            selectinload(Video.video_directors),
        )
        .filter(Video.id == video_id, Video.status == VideoStatus.PUBLISHED)
    )
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Increment view count (should be done asynchronously in production)
    video.view_count += 1
    await db.commit()

    return video


@router.get("/{video_id}/download")
async def get_video_download_url(
    video_id: int,
    quality: str = Query("720p", regex="^(1080p|720p|480p|360p|original)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a presigned download URL for a video

    Args:
        video_id: Video ID
        quality: Video quality (1080p/720p/480p/360p/original)
        current_user: Current authenticated user

    Returns:
        {
            "download_url": "https://minio.../video.mp4?...",
            "expires_in": 86400,  // seconds
            "quality": "720p",
            "file_size": 1024000000  // bytes (optional)
        }

    Raises:
        404: Video not found or not published
        403: User not logged in (handled by dependency)
    """
    # Get video
    result = await db.execute(
        select(Video).filter(
            Video.id == video_id,
            Video.status == VideoStatus.PUBLISHED
        )
    )
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Determine file path based on quality
    if quality == "original":
        # Original uploaded file
        object_name = f"videos/{video_id}/original.mp4"
    else:
        # HLS transcoded version - use the highest available quality
        if video.av1_resolutions and quality in video.av1_resolutions:
            # Use AV1 if available
            object_name = f"videos/{video_id}/av1/{quality}/video.mp4"
        else:
            # Fallback to H.264
            object_name = f"videos/{video_id}/h264/{quality}/video.mp4"

    # Generate presigned URL (valid for 24 hours)
    try:
        download_url = minio_client.get_presigned_url(
            object_name=object_name,
            expires=timedelta(hours=24)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate download URL: {str(e)}"
        )

    # Get file size (optional)
    try:
        file_size = minio_client.get_object_size(object_name)
    except:
        file_size = None

    return {
        "download_url": download_url,
        "expires_in": 86400,  # 24 hours in seconds
        "quality": quality,
        "file_size": file_size,
        "video_title": video.title,
    }

