from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.favorite_folder import FavoriteFolder
from app.models.user_activity import Favorite
from app.models.video import Video
from app.schemas.favorite_folder import (
    FavoriteFolderCreate,
    FavoriteFolderUpdate,
    FavoriteFolderResponse,
    FavoriteFolderWithVideos,
    MoveFavoriteToFolder,
    BatchMoveFavoritesToFolder,
)
from app.schemas.video import VideoListResponse
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.post("/folders", response_model=FavoriteFolderResponse, status_code=status.HTTP_201_CREATED)
async def create_favorite_folder(
    folder_data: FavoriteFolderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new favorite folder

    - **name**: Folder name (required, 1-100 characters)
    - **description**: Folder description (optional, max 500 characters)
    - **is_public**: Whether the folder is public (default: False)
    """
    # Check folder count limit (max 50 folders per user)
    result = await db.execute(
        select(func.count(FavoriteFolder.id)).filter(FavoriteFolder.user_id == current_user.id)
    )
    folder_count = result.scalar()

    if folder_count >= 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 folders allowed per user"
        )

    # Check if folder name already exists for this user
    result = await db.execute(
        select(FavoriteFolder).filter(
            and_(
                FavoriteFolder.user_id == current_user.id,
                FavoriteFolder.name == folder_data.name
            )
        )
    )
    existing_folder = result.scalar_one_or_none()

    if existing_folder:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Folder with this name already exists"
        )

    # Create new folder
    new_folder = FavoriteFolder(
        user_id=current_user.id,
        name=folder_data.name,
        description=folder_data.description,
        is_public=folder_data.is_public,
        is_default=False,
        video_count=0,
    )

    db.add(new_folder)
    await db.commit()
    await db.refresh(new_folder)

    return new_folder


@router.get("/folders", response_model=List[FavoriteFolderResponse])
async def get_favorite_folders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all favorite folders for current user

    Returns folders sorted by: default folder first, then by creation date
    """
    result = await db.execute(
        select(FavoriteFolder)
        .filter(FavoriteFolder.user_id == current_user.id)
        .order_by(FavoriteFolder.is_default.desc(), FavoriteFolder.created_at.asc())
    )
    folders = result.scalars().all()

    # Ensure default folder exists
    if not any(f.is_default for f in folders):
        # Create default folder
        default_folder = FavoriteFolder(
            user_id=current_user.id,
            name="默认收藏夹",
            description="系统默认收藏夹",
            is_public=False,
            is_default=True,
            video_count=0,
        )
        db.add(default_folder)
        await db.commit()
        await db.refresh(default_folder)
        folders = [default_folder] + list(folders)

    return folders


@router.get("/folders/{folder_id}", response_model=FavoriteFolderWithVideos)
async def get_favorite_folder(
    folder_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get favorite folder details with video list

    - Supports pagination
    - Returns folder info and videos
    """
    # Get folder
    result = await db.execute(
        select(FavoriteFolder).filter(
            and_(
                FavoriteFolder.id == folder_id,
                FavoriteFolder.user_id == current_user.id
            )
        )
    )
    folder = result.scalar_one_or_none()

    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )

    # Get videos in folder with pagination
    offset = (page - 1) * page_size

    result = await db.execute(
        select(Video)
        .join(Favorite, Favorite.video_id == Video.id)
        .filter(
            and_(
                Favorite.user_id == current_user.id,
                Favorite.folder_id == folder_id
            )
        )
        .order_by(Favorite.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    videos = result.scalars().all()

    # Convert to response format
    folder_dict = {
        "id": folder.id,
        "user_id": folder.user_id,
        "name": folder.name,
        "description": folder.description,
        "is_public": folder.is_public,
        "is_default": folder.is_default,
        "video_count": folder.video_count,
        "created_at": folder.created_at,
        "updated_at": folder.updated_at,
        "videos": [VideoListResponse.from_orm(v) for v in videos],
    }

    return folder_dict


@router.put("/folders/{folder_id}", response_model=FavoriteFolderResponse)
async def update_favorite_folder(
    folder_id: int,
    folder_data: FavoriteFolderUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update favorite folder

    - Cannot update default folder's name or delete it
    - Name must be unique among user's folders
    """
    # Get folder
    result = await db.execute(
        select(FavoriteFolder).filter(
            and_(
                FavoriteFolder.id == folder_id,
                FavoriteFolder.user_id == current_user.id
            )
        )
    )
    folder = result.scalar_one_or_none()

    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )

    # Check if trying to rename default folder
    if folder.is_default and folder_data.name is not None and folder_data.name != folder.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot rename default folder"
        )

    # Check name uniqueness if renaming
    if folder_data.name and folder_data.name != folder.name:
        result = await db.execute(
            select(FavoriteFolder).filter(
                and_(
                    FavoriteFolder.user_id == current_user.id,
                    FavoriteFolder.name == folder_data.name,
                    FavoriteFolder.id != folder_id
                )
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Folder with this name already exists"
            )

    # Update fields
    update_data = folder_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(folder, field, value)

    await db.commit()
    await db.refresh(folder)

    return folder


@router.delete("/folders/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite_folder(
    folder_id: int,
    move_to_default: bool = Query(True, description="Move videos to default folder"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete favorite folder

    - Cannot delete default folder
    - Options:
      - move_to_default=True: Move all videos to default folder
      - move_to_default=False: Delete all favorites in this folder
    """
    # Get folder
    result = await db.execute(
        select(FavoriteFolder).filter(
            and_(
                FavoriteFolder.id == folder_id,
                FavoriteFolder.user_id == current_user.id
            )
        )
    )
    folder = result.scalar_one_or_none()

    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )

    if folder.is_default:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete default folder"
        )

    if move_to_default:
        # Get or create default folder
        result = await db.execute(
            select(FavoriteFolder).filter(
                and_(
                    FavoriteFolder.user_id == current_user.id,
                    FavoriteFolder.is_default == True
                )
            )
        )
        default_folder = result.scalar_one_or_none()

        if not default_folder:
            default_folder = FavoriteFolder(
                user_id=current_user.id,
                name="默认收藏夹",
                description="系统默认收藏夹",
                is_public=False,
                is_default=True,
                video_count=0,
            )
            db.add(default_folder)
            await db.flush()

        # Move all favorites to default folder
        await db.execute(
            Favorite.__table__.update()
            .where(
                and_(
                    Favorite.user_id == current_user.id,
                    Favorite.folder_id == folder_id
                )
            )
            .values(folder_id=default_folder.id)
        )

        # Update video counts
        result = await db.execute(
            select(func.count(Favorite.id)).filter(Favorite.folder_id == folder_id)
        )
        moved_count = result.scalar()
        default_folder.video_count += moved_count
    else:
        # Delete all favorites in this folder
        await db.execute(
            delete(Favorite).where(
                and_(
                    Favorite.user_id == current_user.id,
                    Favorite.folder_id == folder_id
                )
            )
        )

    # Delete folder
    await db.delete(folder)
    await db.commit()

    return None


@router.post("/move", status_code=status.HTTP_200_OK)
async def move_favorite_to_folder(
    move_data: MoveFavoriteToFolder,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Move a favorite to another folder

    - **favorite_id**: The favorite to move
    - **target_folder_id**: Target folder (None for default folder)
    """
    # Get favorite
    result = await db.execute(
        select(Favorite).filter(
            and_(
                Favorite.id == move_data.favorite_id,
                Favorite.user_id == current_user.id
            )
        )
    )
    favorite = result.scalar_one_or_none()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )

    # Validate target folder
    if move_data.target_folder_id:
        result = await db.execute(
            select(FavoriteFolder).filter(
                and_(
                    FavoriteFolder.id == move_data.target_folder_id,
                    FavoriteFolder.user_id == current_user.id
                )
            )
        )
        target_folder = result.scalar_one_or_none()

        if not target_folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target folder not found"
            )

    # Update folder_id
    old_folder_id = favorite.folder_id
    favorite.folder_id = move_data.target_folder_id

    # Update video counts
    if old_folder_id:
        result = await db.execute(
            select(FavoriteFolder).filter(FavoriteFolder.id == old_folder_id)
        )
        old_folder = result.scalar_one_or_none()
        if old_folder:
            old_folder.video_count = max(0, old_folder.video_count - 1)

    if move_data.target_folder_id:
        result = await db.execute(
            select(FavoriteFolder).filter(FavoriteFolder.id == move_data.target_folder_id)
        )
        new_folder = result.scalar_one_or_none()
        if new_folder:
            new_folder.video_count += 1

    await db.commit()

    return {"message": "Favorite moved successfully"}


@router.post("/batch-move", status_code=status.HTTP_200_OK)
async def batch_move_favorites_to_folder(
    move_data: BatchMoveFavoritesToFolder,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Batch move favorites to another folder

    - **favorite_ids**: List of favorite IDs to move
    - **target_folder_id**: Target folder (None for default folder)
    """
    # Validate target folder
    if move_data.target_folder_id:
        result = await db.execute(
            select(FavoriteFolder).filter(
                and_(
                    FavoriteFolder.id == move_data.target_folder_id,
                    FavoriteFolder.user_id == current_user.id
                )
            )
        )
        target_folder = result.scalar_one_or_none()

        if not target_folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target folder not found"
            )

    # Get all favorites
    result = await db.execute(
        select(Favorite).filter(
            and_(
                Favorite.id.in_(move_data.favorite_ids),
                Favorite.user_id == current_user.id
            )
        )
    )
    favorites = result.scalars().all()

    if len(favorites) != len(move_data.favorite_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Some favorites not found"
        )

    # Track folder changes for count updates
    folder_changes = {}

    for favorite in favorites:
        old_folder_id = favorite.folder_id

        # Decrement old folder count
        if old_folder_id:
            folder_changes[old_folder_id] = folder_changes.get(old_folder_id, 0) - 1

        # Increment new folder count
        if move_data.target_folder_id:
            folder_changes[move_data.target_folder_id] = folder_changes.get(move_data.target_folder_id, 0) + 1

        # Update favorite
        favorite.folder_id = move_data.target_folder_id

    # Update folder counts
    for folder_id, change in folder_changes.items():
        result = await db.execute(
            select(FavoriteFolder).filter(FavoriteFolder.id == folder_id)
        )
        folder = result.scalar_one_or_none()
        if folder:
            folder.video_count = max(0, folder.video_count + change)

    await db.commit()

    return {"message": f"Successfully moved {len(favorites)} favorites"}
