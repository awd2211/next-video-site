from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from app.database import get_db
from app.models.video import Video, VideoStatus
from app.schemas.video import VideoListResponse, PaginatedResponse
from app.utils.cache import Cache
import hashlib

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def search_videos(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Search videos by title (cached for 5 minutes)"""
    # 生成缓存键（使用查询参数的哈希）
    query_hash = hashlib.md5(f"{q}:{page}:{page_size}".encode()).hexdigest()
    cache_key = f"search_results:{query_hash}"

    # 尝试从缓存获取
    cached = await Cache.get(cache_key)
    if cached is not None:
        return cached

    search_pattern = f"%{q}%"
    query = select(Video).filter(
        Video.status == VideoStatus.PUBLISHED,
        or_(
            Video.title.ilike(search_pattern),
            Video.original_title.ilike(search_pattern),
            Video.description.ilike(search_pattern),
        )
    )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
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
        "items": [VideoListResponse.model_validate(v) for v in videos],
    }

    # 缓存5分钟
    await Cache.set(cache_key, response, ttl=300)

    return response
