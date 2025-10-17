"""
API endpoints for shared watchlist feature
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.shared_watchlist import SharedWatchlist
from app.models.user import User
from app.models.video import Video
from app.schemas.shared_watchlist import (
    SharedWatchlistCreate,
    SharedWatchlistPublicResponse,
    SharedWatchlistResponse,
    SharedWatchlistUpdate,
    ShareLinkResponse,
)
from app.schemas.video import VideoListResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/shared-watchlist", tags=["Shared Watchlist"])


@router.post("/create", response_model=ShareLinkResponse)
async def create_shared_watchlist(
    data: SharedWatchlistCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a shareable link for user's watchlist
    """
    # Validate video IDs exist
    result = await db.execute(select(Video.id).where(Video.id.in_(data.video_ids)))
    existing_ids = {row[0] for row in result.all()}

    if len(existing_ids) != len(data.video_ids):
        raise HTTPException(status_code=400, detail="Some video IDs are invalid")

    # Generate unique share token
    share_token = SharedWatchlist.generate_share_token()

    # Calculate expiration
    expires_at = None
    if data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=data.expires_in_days)

    # Create shared watchlist
    shared_list = SharedWatchlist(
        user_id=current_user.id,
        share_token=share_token,
        title=data.title,
        description=data.description,
        video_ids=",".join(map(str, data.video_ids)),
        expires_at=expires_at,
    )

    db.add(shared_list)
    await db.commit()
    await db.refresh(shared_list)

    # Generate share URL
    base_url = str(request.base_url).rstrip("/")
    share_url = f"{base_url}/shared/{share_token}"

    return ShareLinkResponse(
        share_token=share_token,
        share_url=share_url,
        title=data.title,
        expires_at=expires_at,
    )


@router.get("/my-shares", response_model=list[SharedWatchlistResponse])
async def get_my_shared_lists(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all shared lists created by current user
    """
    result = await db.execute(
        select(SharedWatchlist)
        .where(SharedWatchlist.user_id == current_user.id)
        .order_by(SharedWatchlist.created_at.desc())
    )
    shared_lists = result.scalars().all()

    # Convert video_ids string to list
    response = []
    for shared_list in shared_lists:
        video_ids = [int(vid) for vid in shared_list.video_ids.split(",") if vid]
        response.append(
            SharedWatchlistResponse(
                id=shared_list.id,
                user_id=shared_list.user_id,
                share_token=shared_list.share_token,
                title=shared_list.title,
                description=shared_list.description,
                video_ids=video_ids,
                is_active=shared_list.is_active,
                view_count=shared_list.view_count,
                created_at=shared_list.created_at,
                updated_at=shared_list.updated_at,
                expires_at=shared_list.expires_at,
            )
        )

    return response


@router.patch("/{share_token}", response_model=SharedWatchlistResponse)
async def update_shared_watchlist(
    share_token: str,
    data: SharedWatchlistUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a shared watchlist (only by owner)
    """
    result = await db.execute(
        select(SharedWatchlist).where(SharedWatchlist.share_token == share_token)
    )
    shared_list = result.scalar_one_or_none()

    if not shared_list:
        raise HTTPException(status_code=404, detail="Shared list not found")

    if shared_list.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this list")

    # Update fields
    if data.title is not None:
        shared_list.title = data.title
    if data.description is not None:
        shared_list.description = data.description
    if data.video_ids is not None:
        # Validate video IDs
        result = await db.execute(select(Video.id).where(Video.id.in_(data.video_ids)))
        existing_ids = {row[0] for row in result.all()}
        if len(existing_ids) != len(data.video_ids):
            raise HTTPException(status_code=400, detail="Some video IDs are invalid")
        shared_list.video_ids = ",".join(map(str, data.video_ids))
    if data.is_active is not None:
        shared_list.is_active = data.is_active

    await db.commit()
    await db.refresh(shared_list)

    video_ids = [int(vid) for vid in shared_list.video_ids.split(",") if vid]
    return SharedWatchlistResponse(
        id=shared_list.id,
        user_id=shared_list.user_id,
        share_token=shared_list.share_token,
        title=shared_list.title,
        description=shared_list.description,
        video_ids=video_ids,
        is_active=shared_list.is_active,
        view_count=shared_list.view_count,
        created_at=shared_list.created_at,
        updated_at=shared_list.updated_at,
        expires_at=shared_list.expires_at,
    )


@router.delete("/{share_token}")
async def delete_shared_watchlist(
    share_token: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a shared watchlist (only by owner)
    """
    result = await db.execute(
        select(SharedWatchlist).where(SharedWatchlist.share_token == share_token)
    )
    shared_list = result.scalar_one_or_none()

    if not shared_list:
        raise HTTPException(status_code=404, detail="Shared list not found")

    if shared_list.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this list")

    await db.delete(shared_list)
    await db.commit()

    return {"message": "Shared list deleted successfully"}


@router.get("/{share_token}", response_model=dict)
async def get_shared_watchlist(
    share_token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a shared watchlist by token (public endpoint)
    Returns both list metadata and video details
    """
    result = await db.execute(
        select(SharedWatchlist, User.username)
        .join(User, SharedWatchlist.user_id == User.id)
        .where(SharedWatchlist.share_token == share_token)
    )
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Shared list not found")

    shared_list, username = row

    # Check if expired
    if shared_list.expires_at and shared_list.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="This shared list has expired")

    # Check if active
    if not shared_list.is_active:
        raise HTTPException(status_code=403, detail="This shared list is no longer available")

    # Increment view count
    shared_list.view_count += 1
    await db.commit()

    # Get video details
    video_ids = [int(vid) for vid in shared_list.video_ids.split(",") if vid]
    result = await db.execute(
        select(Video).where(Video.id.in_(video_ids))
    )
    videos = result.scalars().all()

    # Create video dict for ordering
    video_dict = {video.id: video for video in videos}
    ordered_videos = [video_dict[vid] for vid in video_ids if vid in video_dict]

    # Convert to response
    video_responses = [
        VideoListResponse(
            id=video.id,
            title=video.title,
            slug=video.slug,
            description=video.description,
            video_type=video.video_type,
            cover_image=video.cover_image,
            trailer_url=video.trailer_url,
            duration=video.duration,
            release_year=video.release_year,
            average_rating=video.average_rating,
            view_count=video.view_count,
            is_featured=video.is_featured,
            country=None,  # Optional, can be loaded if needed
            categories=[],  # Optional, can be loaded if needed
            created_at=video.created_at,
        )
        for video in ordered_videos
    ]

    list_info = SharedWatchlistPublicResponse(
        share_token=shared_list.share_token,
        title=shared_list.title,
        description=shared_list.description,
        video_ids=video_ids,
        view_count=shared_list.view_count,
        created_at=shared_list.created_at,
        username=username,
    )

    return {
        "list_info": list_info,
        "videos": video_responses,
    }
