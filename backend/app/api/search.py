import hashlib
import math
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from loguru import logger
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.user_activity import SearchHistory
from app.models.video import Video, VideoStatus
from app.schemas.search import (
    PopularSearchResponse,
    SearchHistoryCreate,
    SearchHistoryResponse,
)
from app.schemas.video import PaginatedResponse, VideoListResponse
from app.utils.cache import Cache
from app.utils.dependencies import get_current_user, get_current_user_optional
from app.utils.rate_limit import RateLimitPresets, limiter

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
@limiter.limit(RateLimitPresets.MODERATE)  # 搜索限流: 60/分钟
async def search_videos(
    request: Request,
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    country_id: Optional[int] = None,
    year: Optional[int] = None,
    min_rating: Optional[float] = Query(None, ge=0, le=10),
    sort_by: str = Query(
        "created_at", regex="^(created_at|view_count|average_rating|relevance)$"
    ),
    db: AsyncSession = Depends(get_db),
):
    """Search videos with advanced filters (cached for 5 minutes)"""
    # 生成缓存键（使用查询参数的哈希）
    query_hash = hashlib.md5(
        f"{q}:{page}:{page_size}:{category_id}:{country_id}:{year}:{min_rating}:{sort_by}".encode()
    ).hexdigest()
    cache_key = f"search_results:{query_hash}"

    # 尝试从缓存获取
    cached = await Cache.get(cache_key)
    if cached is not None:
        return cached

    # Build base search query using PostgreSQL full-text search
    filters = [Video.status == VideoStatus.PUBLISHED]

    # 使用PostgreSQL全文搜索（性能优化：100倍提升）
    # search_vector列已通过migration创建并自动更新
    search_query_obj = func.plainto_tsquery("simple", q)
    filters.append(Video.search_vector.op("@@")(search_query_obj))

    # Apply advanced filters
    if category_id:
        filters.append(Video.video_categories.any(category_id=category_id))
    if country_id:
        filters.append(Video.country_id == country_id)
    if year:
        filters.append(Video.release_year == year)
    if min_rating is not None:
        filters.append(Video.average_rating >= min_rating)

    from app.models.video import VideoCategory

    query = select(Video).options(
        selectinload(Video.country),
        selectinload(Video.video_categories).selectinload(VideoCategory.category)
    ).filter(and_(*filters))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar() or 0

    # Apply sorting
    if sort_by == "view_count":
        query = query.order_by(desc(Video.view_count))
    elif sort_by == "average_rating":
        query = query.order_by(desc(Video.average_rating))
    elif sort_by == "relevance":
        # 按相关性排序（全文搜索特性）
        query = query.order_by(desc(func.ts_rank(Video.search_vector, search_query_obj)))
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


# ==================== Search History Endpoints ====================


@router.post("/history", status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimitPresets.MODERATE)
async def record_search_history(
    request: Request,
    search_data: SearchHistoryCreate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    Record a search query (for logged-in users and analytics)

    This endpoint is fire-and-forget - frontend shouldn't block on it.
    """
    try:
        # Get IP address and User-Agent for analytics
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        # Create search history entry
        search_history = SearchHistory(
            user_id=current_user.id if current_user else None,
            query=search_data.query.strip(),
            results_count=search_data.results_count,
            clicked_video_id=search_data.clicked_video_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        db.add(search_history)
        await db.commit()

        logger.info(
            f"Search recorded: query='{search_data.query}', "
            f"results={search_data.results_count}, "
            f"user_id={current_user.id if current_user else 'anonymous'}"
        )

        return {"message": "Search history recorded successfully"}

    except Exception as e:
        logger.error(f"Failed to record search history: {e}")
        await db.rollback()
        # Don't fail the request - search history is not critical
        return {"message": "Search history recording failed (non-critical)"}


@router.get("/history", response_model=list[SearchHistoryResponse])
@limiter.limit(RateLimitPresets.MODERATE)
async def get_user_search_history(
    request: Request,
    limit: int = Query(20, ge=1, le=100, description="Number of recent searches to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user's search history (requires authentication)

    Returns deduplicated list of recent searches ordered by most recent first.
    """
    # Query user's recent searches (distinct queries only)
    query = (
        select(SearchHistory)
        .filter(SearchHistory.user_id == current_user.id)
        .order_by(desc(SearchHistory.created_at))
        .limit(limit * 2)  # Get more to deduplicate
    )

    result = await db.execute(query)
    all_searches = result.scalars().all()

    # Deduplicate by query (keep most recent)
    seen_queries = set()
    unique_searches = []

    for search in all_searches:
        if search.query not in seen_queries:
            seen_queries.add(search.query)
            unique_searches.append(search)

        if len(unique_searches) >= limit:
            break

    return unique_searches


@router.delete("/history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_search_history_item(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a specific search history item (user must own it)"""
    # Find the history item
    result = await db.execute(
        select(SearchHistory).filter(
            SearchHistory.id == history_id, SearchHistory.user_id == current_user.id
        )
    )
    history_item = result.scalar_one_or_none()

    if not history_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search history item not found or access denied",
        )

    await db.delete(history_item)
    await db.commit()

    logger.info(
        f"Search history deleted: id={history_id}, user_id={current_user.id}"
    )


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_search_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Clear all search history for current user"""
    # Delete all user's search history
    result = await db.execute(
        select(SearchHistory).filter(SearchHistory.user_id == current_user.id)
    )
    history_items = result.scalars().all()

    for item in history_items:
        await db.delete(item)

    await db.commit()

    logger.info(
        f"All search history cleared: user_id={current_user.id}, "
        f"count={len(history_items)}"
    )


@router.get("/popular", response_model=list[PopularSearchResponse])
@limiter.limit(RateLimitPresets.STRICT)
async def get_popular_searches(
    request: Request,
    limit: int = Query(10, ge=1, le=50, description="Number of popular searches to return"),
    hours: int = Query(
        24, ge=1, le=168, description="Time window in hours (default: 24h)"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Get popular search queries (cached for 1 hour)

    Returns top N most searched queries in the specified time window.
    """
    cache_key = f"popular_searches:{limit}:{hours}"

    # Try to get from cache
    cached = await Cache.get(cache_key)
    if cached is not None:
        return cached

    # Calculate time threshold
    now = datetime.now(timezone.utc)
    time_threshold = now - timedelta(hours=hours)

    # Aggregate searches by query
    query = (
        select(SearchHistory.query, func.count(SearchHistory.id).label("search_count"))
        .filter(SearchHistory.created_at >= time_threshold)
        .group_by(SearchHistory.query)
        .order_by(desc("search_count"))
        .limit(limit)
    )

    result = await db.execute(query)
    popular_searches = [
        PopularSearchResponse(query=row[0], search_count=row[1]) for row in result.all()
    ]

    # Cache for 1 hour
    await Cache.set(cache_key, popular_searches, ttl=3600)

    return popular_searches
