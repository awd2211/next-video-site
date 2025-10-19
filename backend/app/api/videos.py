import math
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from loguru import logger
from sqlalchemy import desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.video import (
    Video,
    VideoActor,
    VideoCategory,
    VideoDirector,
    VideoStatus,
    VideoTag,
)
from app.schemas.video import PaginatedResponse, VideoDetailResponse, VideoListResponse
from app.utils.cache import Cache
from app.utils.dependencies import get_current_user
from app.utils.minio_client import minio_client
from app.utils.rate_limit import limiter, RateLimitPresets

router = APIRouter()

# TODO(human): 为以下三个端点添加限流装饰器
# 1. list_videos - 使用 RateLimitPresets.RELAXED
# 2. get_trending_videos - 使用 RateLimitPresets.RELAXED
# 3. get_video_detail (在文件后面) - 使用 RateLimitPresets.MODERATE
# 参考格式: @limiter.limit(RateLimitPresets.RELAXED)
# 记得在函数参数中添加 request: Request

@router.get("", response_model=PaginatedResponse)
async def list_videos(
    request: Request,  # 限流器需要此参数
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    video_type: Optional[str] = None,
    country_id: Optional[int] = None,
    category_id: Optional[int] = None,
    year: Optional[int] = None,
    sort_by: str = Query(
        "created_at", regex="^(created_at|view_count|average_rating)$"
    ),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated list of published videos (cached for 5 minutes)"""
    # 生成缓存键（包含所有过滤参数）
    cache_key = f"videos_list:{page}:{page_size}:{video_type or 'all'}:{country_id or 'all'}:{category_id or 'all'}:{year or 'all'}:{sort_by}"

    # 尝试从缓存获取
    cached = await Cache.get(cache_key)
    if cached is not None:
        return cached

    # 预加载关联数据，避免N+1查询和延迟加载问题
    query = (
        select(Video)
        .options(
            selectinload(Video.country),
            selectinload(Video.video_categories).selectinload(VideoCategory.category)
        )
        .filter(Video.status == VideoStatus.PUBLISHED)
    )

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
    total = result.scalar() or 0

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

    response = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size) if page_size > 0 and total > 0 else 0,
        "items": [VideoListResponse.model_validate(v) for v in videos],
    }

    # 缓存5分钟
    await Cache.set(cache_key, response, ttl=300)

    return response


@router.get("/trending", response_model=PaginatedResponse)
async def get_trending_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    time_range: str = Query("all", regex="^(today|week|all|rising)$"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get trending videos with time-based filtering (cached for 10 minutes)

    Args:
        page: Page number
        page_size: Items per page
        time_range: Time range filter - "today", "week", "all", or "rising"
    """
    # 生成缓存键（包含time_range）
    cache_key = f"trending_videos:page_{page}:size_{page_size}:range_{time_range}"

    # 尝试从缓存获取
    cached = await Cache.get(cache_key)
    if cached is not None:
        return cached

    # 从数据库查询（预加载关联数据避免延迟加载问题）
    query = (
        select(Video)
        .options(
            selectinload(Video.country),
            selectinload(Video.video_categories).selectinload(VideoCategory.category)
        )
        .filter(Video.status == VideoStatus.PUBLISHED)
    )

    # Time-based filtering
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)

    if time_range == "today":
        # Videos from last 24 hours
        yesterday = now - timedelta(days=1)
        query = query.filter(Video.created_at >= yesterday)
        # Sort by view count for today's trending
        query = query.order_by(desc(Video.view_count), desc(Video.created_at))
    elif time_range == "week":
        # Videos from last 7 days
        week_ago = now - timedelta(days=7)
        query = query.filter(Video.created_at >= week_ago)
        # Sort by view count for this week's trending
        query = query.order_by(desc(Video.view_count), desc(Video.created_at))
    elif time_range == "rising":
        # Rising videos: recent uploads with good view velocity
        # Videos from last 3 days, sorted by view count (these are "rising")
        three_days_ago = now - timedelta(days=3)
        query = query.filter(Video.created_at >= three_days_ago)
        # Sort by view count to get rising stars
        query = query.order_by(desc(Video.view_count), desc(Video.created_at))
    else:  # "all"
        # All time trending - just by view count
        query = query.order_by(desc(Video.view_count))

    # Count total with same filters
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    videos = result.scalars().all()

    response = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size) if page_size > 0 and total > 0 else 0,
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

    # 从数据库查询（预加载关联数据避免延迟加载问题）
    query = (
        select(Video)
        .options(
            selectinload(Video.country),
            selectinload(Video.video_categories).selectinload(VideoCategory.category)
        )
        .filter(Video.status == VideoStatus.PUBLISHED, Video.is_featured.is_(True))
        .order_by(desc(Video.sort_order), desc(Video.created_at))
    )

    # Count total
    count_query = select(func.count()).select_from(
        select(Video)
        .filter(Video.status == VideoStatus.PUBLISHED, Video.is_featured.is_(True))
        .subquery()
    )
    result = await db.execute(count_query)
    total = result.scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    videos = result.scalars().all()

    response = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size) if page_size > 0 and total > 0 else 0,
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

    # 从数据库查询（预加载关联数据避免延迟加载问题）
    query = (
        select(Video)
        .options(
            selectinload(Video.country),
            selectinload(Video.video_categories).selectinload(VideoCategory.category)
        )
        .filter(Video.status == VideoStatus.PUBLISHED, Video.is_recommended.is_(True))
        .order_by(desc(Video.sort_order), desc(Video.created_at))
    )

    # Count total
    count_query = select(func.count()).select_from(
        select(Video)
        .filter(Video.status == VideoStatus.PUBLISHED, Video.is_recommended.is_(True))
        .subquery()
    )
    result = await db.execute(count_query)
    total = result.scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    videos = result.scalars().all()

    response = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size) if page_size > 0 and total > 0 else 0,
        "items": [VideoListResponse.model_validate(v) for v in videos],
    }

    # 缓存15分钟
    await Cache.set(cache_key, response, ttl=900)

    return response


@router.get("/{video_id}", response_model=VideoDetailResponse)
async def get_video(
    video_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Get video details with eagerly loaded relationships"""
    # 尝试从缓存获取（5分钟TTL）
    cache_key = f"video_detail:{video_id}"
    cached = await Cache.get(cache_key)
    if cached is not None:
        # 仍然异步增加浏览量
        async def increment_view():
            from app.database import AsyncSessionLocal

            async with AsyncSessionLocal() as session:
                try:
                    await session.execute(
                        update(Video)
                        .where(Video.id == video_id)
                        .values(view_count=Video.view_count + 1)
                    )
                    await session.commit()
                except Exception as e:
                    logger.error(f"Failed to increment view count: {e}", exc_info=True)

        background_tasks.add_task(increment_view)
        return cached

    # 使用selectinload预加载所有关联数据，避免N+1查询问题
    result = await db.execute(
        select(Video)
        .options(
            selectinload(Video.country),
            selectinload(Video.video_categories).selectinload(VideoCategory.category),
            selectinload(Video.video_tags).selectinload(VideoTag.tag),
            selectinload(Video.video_actors).selectinload(VideoActor.actor),
            selectinload(Video.video_directors).selectinload(VideoDirector.director),
        )
        .filter(Video.id == video_id, Video.status == VideoStatus.PUBLISHED)
    )
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Manually extract relationships from association tables
    video.categories = [vc.category for vc in video.video_categories if vc.category]
    video.tags = [vt.tag for vt in video.video_tags if vt.tag]
    video.actors = [va.actor for va in video.video_actors if va.actor]
    video.directors = [vd.director for vd in video.video_directors if vd.director]

    # 构建响应并缓存
    response = VideoDetailResponse.model_validate(video)
    await Cache.set(cache_key, response, ttl=300)  # 缓存5分钟

    # 使用后台任务异步更新浏览量（不缓存时）
    async def increment_view_count():
        from app.database import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            try:
                await session.execute(
                    update(Video)
                    .where(Video.id == video_id)
                    .values(view_count=Video.view_count + 1)
                )
                await session.commit()
            except Exception as e:
                logger.error(f"Failed to increment view count: {e}", exc_info=True)

    background_tasks.add_task(increment_view_count)

    return response


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
            Video.id == video_id, Video.status == VideoStatus.PUBLISHED
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
            object_name=object_name, expires=timedelta(hours=24)
        )
    except Exception:
        # 不泄露详细错误信息
        raise HTTPException(status_code=500, detail="Failed to generate download URL")

    # Get file size (optional)
    try:
        file_size = minio_client.get_object_size(object_name)
    except Exception:
        file_size = None

    return {
        "download_url": download_url,
        "expires_in": 86400,  # 24 hours in seconds
        "quality": quality,
        "file_size": file_size,
        "video_title": video.title,
    }
