from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.video import Actor
from app.models.user import AdminUser
from app.schemas.admin_content import (
    ActorCreate,
    ActorUpdate,
    ActorAdminResponse,
    PaginatedActorAdminResponse,
)
from app.utils.dependencies import get_current_admin_user
from app.utils.cache import Cache

router = APIRouter()


@router.get("/", response_model=PaginatedActorAdminResponse)
async def get_actors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", description="Search actors by name"),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all actors with pagination and search"""
    query = select(Actor)

    if search:
        query = query.where(Actor.name.ilike(f"%{search}%"))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.order_by(Actor.name).offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    actors = result.scalars().all()

    items = [ActorAdminResponse.model_validate(actor) for actor in actors]

    return PaginatedActorAdminResponse(
        total=total, page=page, page_size=page_size, items=items
    )


@router.post(
    "/", response_model=ActorAdminResponse, status_code=status.HTTP_201_CREATED
)
async def create_actor(
    actor_data: ActorCreate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new actor"""
    # Create actor
    actor = Actor(**actor_data.model_dump())
    db.add(actor)
    await db.commit()
    await db.refresh(actor)

    # 清除演员缓存
    await Cache.delete_pattern("actors_list:*")

    return ActorAdminResponse.model_validate(actor)


@router.get("/{actor_id}", response_model=ActorAdminResponse)
async def get_actor(
    actor_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get actor by ID"""
    result = await db.execute(select(Actor).where(Actor.id == actor_id))
    actor = result.scalar_one_or_none()

    if not actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Actor not found"
        )

    return ActorAdminResponse.model_validate(actor)


@router.put("/{actor_id}", response_model=ActorAdminResponse)
async def update_actor(
    actor_id: int,
    actor_data: ActorUpdate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an actor"""
    result = await db.execute(select(Actor).where(Actor.id == actor_id))
    actor = result.scalar_one_or_none()

    if not actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Actor not found"
        )

    # Update fields
    update_data = actor_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(actor, field, value)

    await db.commit()
    await db.refresh(actor)

    # 清除演员缓存
    await Cache.delete_pattern("actors_list:*")

    return ActorAdminResponse.model_validate(actor)


@router.delete("/{actor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_actor(
    actor_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an actor"""
    result = await db.execute(select(Actor).where(Actor.id == actor_id))
    actor = result.scalar_one_or_none()

    if not actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Actor not found"
        )

    await db.delete(actor)
    await db.commit()

    # 清除演员缓存
    await Cache.delete_pattern("actors_list:*")

    return None
