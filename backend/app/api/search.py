import hashlib
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.video import Video, VideoStatus
from app.schemas.video import PaginatedResponse, VideoListResponse
from app.utils.cache import Cache
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
        "created_at", regex="^(created_at|view_count|average_rating)$"
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
    # 使用tsquery进行全文搜索，性能远超ILIKE
    filters = [Video.status == VideoStatus.PUBLISHED]

    # 使用ILIKE搜索（稳定可靠）
    # 注：如果需要全文搜索，确保search_vector列已正确配置和填充
    search_pattern = f"%{q}%"
    filters.append(
        or_(
            Video.title.ilike(search_pattern),
            Video.original_title.ilike(search_pattern),
            Video.description.ilike(search_pattern),
        )
    )

    # Apply advanced filters
    if category_id:
        filters.append(Video.video_categories.any(category_id=category_id))
    if country_id:
        filters.append(Video.country_id == country_id)
    if year:
        filters.append(Video.release_year == year)
    if min_rating is not None:
        filters.append(Video.average_rating >= min_rating)

    query = select(Video).options(selectinload(Video.country)).filter(and_(*filters))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar() or 0

    # Apply sorting
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
        "items": [VideoListResponse.model_validate(v) for v in videos],
    }

    # 缓存5分钟
    await Cache.set(cache_key, response, ttl=300)

    return response
