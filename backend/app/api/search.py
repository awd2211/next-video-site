from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from app.database import get_db
from app.models.video import Video, VideoStatus
from app.schemas.video import VideoListResponse, PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def search_videos(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Search videos by title"""
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

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": videos,
    }
