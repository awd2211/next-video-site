from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.user import User
from app.models.user_activity import Favorite
from app.models.video import Video
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.video import VideoListResponse, PaginatedResponse
from app.utils.dependencies import get_current_active_user
from app.utils.cache import Cache

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile"""
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.avatar is not None:
        current_user.avatar = user_update.avatar

    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.get("/me/favorites", response_model=PaginatedResponse)
async def get_user_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's favorite videos (cached for 2 minutes)"""
    # 生成缓存键
    cache_key = f"user_favorites:{current_user.id}:page_{page}:size_{page_size}"

    # 尝试从缓存获取
    cached = await Cache.get(cache_key)
    if cached is not None:
        return cached

    # 查询收藏的视频
    query = (
        select(Video)
        .join(Favorite, Favorite.video_id == Video.id)
        .filter(Favorite.user_id == current_user.id)
        .order_by(desc(Favorite.created_at))
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

    # 缓存2分钟
    await Cache.set(cache_key, response, ttl=120)

    return response


@router.post("/me/favorites/{video_id}", status_code=status.HTTP_201_CREATED)
async def add_to_favorites(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Add video to favorites"""
    # 检查视频是否存在
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # 检查是否已收藏
    result = await db.execute(
        select(Favorite).filter(
            Favorite.user_id == current_user.id, Favorite.video_id == video_id
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Video already in favorites")

    # 创建收藏
    favorite = Favorite(user_id=current_user.id, video_id=video_id)
    db.add(favorite)
    await db.commit()

    # 清除用户收藏缓存
    await Cache.delete_pattern(f"user_favorites:{current_user.id}:*")

    return {"message": "Added to favorites"}


@router.delete("/me/favorites/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_favorites(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove video from favorites"""
    result = await db.execute(
        select(Favorite).filter(
            Favorite.user_id == current_user.id, Favorite.video_id == video_id
        )
    )
    favorite = result.scalar_one_or_none()

    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")

    await db.delete(favorite)
    await db.commit()

    # 清除用户收藏缓存
    await Cache.delete_pattern(f"user_favorites:{current_user.id}:*")

    return None
