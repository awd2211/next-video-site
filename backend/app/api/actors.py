from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.video import Actor, VideoActor, Video
from app.schemas.person import (
    ActorResponse,
    ActorDetailResponse,
    PaginatedActorResponse,
)

router = APIRouter()


@router.get("/", response_model=PaginatedActorResponse)
async def get_actors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", description="Search actors by name"),
    db: AsyncSession = Depends(get_db),
):
    """Get list of actors with pagination and search"""
    # Build query
    query = select(Actor)

    # Apply search filter
    if search:
        query = query.where(Actor.name.ilike(f"%{search}%"))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = (
        query
        .order_by(Actor.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    actors = result.scalars().all()

    items = [ActorResponse.model_validate(actor) for actor in actors]

    return PaginatedActorResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/{actor_id}", response_model=ActorDetailResponse)
async def get_actor(
    actor_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get actor details with their videos"""
    query = (
        select(Actor)
        .where(Actor.id == actor_id)
        .options(selectinload(Actor.video_actors).selectinload(VideoActor.video))
    )

    result = await db.execute(query)
    actor = result.scalar_one_or_none()

    if not actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Actor not found"
        )

    # Get videos featuring this actor
    videos = [va.video for va in actor.video_actors if va.video]

    # Build response
    actor_data = ActorDetailResponse.model_validate(actor)
    actor_data.videos = videos

    return actor_data


@router.get("/{actor_id}/videos", response_model=dict)
async def get_actor_videos(
    actor_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get videos featuring a specific actor"""
    # Verify actor exists
    actor_result = await db.execute(select(Actor).where(Actor.id == actor_id))
    actor = actor_result.scalar_one_or_none()
    if not actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Actor not found"
        )

    # Count total videos
    count_query = (
        select(func.count())
        .select_from(VideoActor)
        .where(VideoActor.actor_id == actor_id)
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated videos
    query = (
        select(Video)
        .join(VideoActor, VideoActor.video_id == Video.id)
        .where(VideoActor.actor_id == actor_id)
        .order_by(Video.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    videos = result.scalars().all()

    from app.schemas.video import VideoListResponse
    items = [VideoListResponse.model_validate(video) for video in videos]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }
