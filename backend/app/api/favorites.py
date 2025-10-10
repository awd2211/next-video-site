from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.user_activity import Favorite
from app.models.user import User
from app.models.video import Video
from app.models.favorite_folder import FavoriteFolder
from app.schemas.user_activity import (
    FavoriteCreate,
    FavoriteResponse,
    PaginatedFavoriteResponse,
)
from app.utils.dependencies import get_current_active_user

router = APIRouter()


@router.post("/", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    favorite_data: FavoriteCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a video to user's favorites"""
    # Verify video exists
    video_result = await db.execute(select(Video).where(Video.id == favorite_data.video_id))
    video = video_result.scalar_one_or_none()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    # Check if already favorited
    existing_result = await db.execute(
        select(Favorite).where(
            and_(
                Favorite.user_id == current_user.id,
                Favorite.video_id == favorite_data.video_id
            )
        )
    )
    existing_favorite = existing_result.scalar_one_or_none()

    if existing_favorite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video already in favorites"
        )

    # Validate folder_id if provided
    folder_id = favorite_data.folder_id
    if folder_id:
        folder_result = await db.execute(
            select(FavoriteFolder).where(
                and_(
                    FavoriteFolder.id == folder_id,
                    FavoriteFolder.user_id == current_user.id
                )
            )
        )
        folder = folder_result.scalar_one_or_none()
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder not found"
            )
    else:
        # Get or create default folder
        folder_result = await db.execute(
            select(FavoriteFolder).where(
                and_(
                    FavoriteFolder.user_id == current_user.id,
                    FavoriteFolder.is_default == True
                )
            )
        )
        folder = folder_result.scalar_one_or_none()

        if not folder:
            # Create default folder
            folder = FavoriteFolder(
                user_id=current_user.id,
                name="默认收藏夹",
                description="系统默认收藏夹",
                is_public=False,
                is_default=True,
                video_count=0,
            )
            db.add(folder)
            await db.flush()

        folder_id = folder.id

    # Create favorite
    favorite = Favorite(
        user_id=current_user.id,
        video_id=favorite_data.video_id,
        folder_id=folder_id
    )
    db.add(favorite)

    # Update video favorite count
    video.favorite_count += 1

    # Update folder video count
    folder.video_count += 1

    await db.commit()
    await db.refresh(favorite)
    await db.refresh(favorite, ["video"])

    return FavoriteResponse.model_validate(favorite)


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a video from user's favorites"""
    result = await db.execute(
        select(Favorite).where(
            and_(
                Favorite.user_id == current_user.id,
                Favorite.video_id == video_id
            )
        )
    )
    favorite = result.scalar_one_or_none()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )

    # Update video favorite count
    video_result = await db.execute(select(Video).where(Video.id == video_id))
    video = video_result.scalar_one_or_none()
    if video and video.favorite_count > 0:
        video.favorite_count -= 1

    # Update folder video count
    if favorite.folder_id:
        folder_result = await db.execute(
            select(FavoriteFolder).where(FavoriteFolder.id == favorite.folder_id)
        )
        folder = folder_result.scalar_one_or_none()
        if folder and folder.video_count > 0:
            folder.video_count -= 1

    await db.delete(favorite)
    await db.commit()

    return None


@router.get("/", response_model=PaginatedFavoriteResponse)
async def get_my_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's favorite videos"""
    # Count total
    count_query = select(func.count()).where(Favorite.user_id == current_user.id)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated favorites with video details
    query = (
        select(Favorite)
        .where(Favorite.user_id == current_user.id)
        .options(selectinload(Favorite.video))
        .order_by(Favorite.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    favorites = result.scalars().all()

    items = [FavoriteResponse.model_validate(fav) for fav in favorites]

    return PaginatedFavoriteResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/check/{video_id}", response_model=dict)
async def check_favorite(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Check if a video is in user's favorites"""
    result = await db.execute(
        select(Favorite).where(
            and_(
                Favorite.user_id == current_user.id,
                Favorite.video_id == video_id
            )
        )
    )
    favorite = result.scalar_one_or_none()

    return {"is_favorited": favorite is not None}
