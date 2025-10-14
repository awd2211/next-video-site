"""
Watchlist (My List) API
Netflix-style "My List" feature for saving videos to watch later
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.video import Video, VideoCategory, VideoStatus
from app.models.watchlist import Watchlist
from app.schemas.watchlist import (
    WatchlistCreate,
    WatchlistReorderRequest,
    WatchlistResponse,
    WatchlistStatusResponse,
    WatchlistWithVideo,
)
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.get("", response_model=list[WatchlistWithVideo])
async def get_my_watchlist(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get user's watchlist (My List)
    Returns list of videos ordered by user's custom position
    """
    # Query watchlist with video details
    query = (
        select(Watchlist)
        .options(
            selectinload(Watchlist.video)
            .selectinload(Video.country),
            selectinload(Watchlist.video)
            .selectinload(Video.video_categories)
            .selectinload(VideoCategory.category),
        )
        .where(Watchlist.user_id == current_user.id)
        .where(Video.status == VideoStatus.PUBLISHED)  # Only show published videos
        .join(Video, Watchlist.video_id == Video.id)
        .order_by(Watchlist.position, Watchlist.created_at.desc())
    )

    result = await db.execute(query)
    watchlist_items = result.scalars().all()

    return watchlist_items


@router.post("", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(
    watchlist_data: WatchlistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add video to watchlist (My List)
    """
    # Check if video exists and is published
    video_query = select(Video).where(
        Video.id == watchlist_data.video_id, Video.status == VideoStatus.PUBLISHED
    )
    result = await db.execute(video_query)
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found or not published"
        )

    # Check if already in watchlist
    check_query = select(Watchlist).where(
        Watchlist.user_id == current_user.id, Watchlist.video_id == watchlist_data.video_id
    )
    result = await db.execute(check_query)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Video already in watchlist",
        )

    # Get max position for new item
    max_position_query = select(Watchlist.position).where(
        Watchlist.user_id == current_user.id
    ).order_by(Watchlist.position.desc()).limit(1)
    result = await db.execute(max_position_query)
    max_position = result.scalar_one_or_none()
    new_position = (max_position or 0) + 1

    # Add to watchlist
    watchlist_entry = Watchlist(
        user_id=current_user.id,
        video_id=watchlist_data.video_id,
        position=new_position,
    )

    db.add(watchlist_entry)
    await db.commit()
    await db.refresh(watchlist_entry)

    return watchlist_entry


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_watchlist(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Remove video from watchlist (My List)
    """
    # Check if in watchlist
    query = select(Watchlist).where(
        Watchlist.user_id == current_user.id, Watchlist.video_id == video_id
    )
    result = await db.execute(query)
    watchlist_entry = result.scalar_one_or_none()

    if not watchlist_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not in watchlist"
        )

    # Delete entry
    await db.delete(watchlist_entry)
    await db.commit()

    return None


@router.get("/check/{video_id}", response_model=WatchlistStatusResponse)
async def check_in_watchlist(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Check if video is in user's watchlist
    """
    query = select(Watchlist).where(
        Watchlist.user_id == current_user.id, Watchlist.video_id == video_id
    )
    result = await db.execute(query)
    watchlist_entry = result.scalar_one_or_none()

    return {
        "in_watchlist": watchlist_entry is not None,
        "watchlist_id": watchlist_entry.id if watchlist_entry else None,
    }


@router.put("/reorder", response_model=dict)
async def reorder_watchlist(
    reorder_data: WatchlistReorderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Reorder watchlist items
    Accepts list of video IDs in desired order
    """
    # Get all user's watchlist items
    query = select(Watchlist).where(Watchlist.user_id == current_user.id)
    result = await db.execute(query)
    watchlist_items = {item.video_id: item for item in result.scalars().all()}

    # Update positions
    for position, video_id in enumerate(reorder_data.video_ids, start=1):
        if video_id in watchlist_items:
            watchlist_items[video_id].position = position

    await db.commit()

    return {"message": "Watchlist reordered successfully"}


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_watchlist(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Clear all items from watchlist
    """
    stmt = delete(Watchlist).where(Watchlist.user_id == current_user.id)
    await db.execute(stmt)
    await db.commit()

    return None
