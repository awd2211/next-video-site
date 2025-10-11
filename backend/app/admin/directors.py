import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import AdminUser
from app.models.video import Director
from app.schemas.admin_content import (
    DirectorAdminResponse,
    DirectorCreate,
    DirectorUpdate,
    PaginatedDirectorAdminResponse,
)
from app.utils.cache import Cache
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


@router.get("/", response_model=PaginatedDirectorAdminResponse)
async def get_directors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", description="Search directors by name"),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all directors with pagination and search"""
    query = select(Director)

    if search:
        query = query.where(Director.name.ilike(f"%{search}%"))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    query = (
        query.order_by(Director.name).offset((page - 1) * page_size).limit(page_size)
    )

    result = await db.execute(query)
    directors = result.scalars().all()

    items = [DirectorAdminResponse.model_validate(director) for director in directors]

    return PaginatedDirectorAdminResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if page_size > 0 and total > 0 else 0,
        items=items,
    )


@router.post(
    "/", response_model=DirectorAdminResponse, status_code=status.HTTP_201_CREATED
)
async def create_director(
    director_data: DirectorCreate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new director"""
    # Create director
    director = Director(**director_data.model_dump())
    db.add(director)
    await db.commit()
    await db.refresh(director)

    # 清除导演缓存
    await Cache.delete_pattern("directors_list:*")

    return DirectorAdminResponse.model_validate(director)


@router.get("/{director_id}", response_model=DirectorAdminResponse)
async def get_director(
    director_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get director by ID"""
    result = await db.execute(select(Director).where(Director.id == director_id))
    director = result.scalar_one_or_none()

    if not director:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Director not found"
        )

    return DirectorAdminResponse.model_validate(director)


@router.put("/{director_id}", response_model=DirectorAdminResponse)
async def update_director(
    director_id: int,
    director_data: DirectorUpdate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a director"""
    result = await db.execute(select(Director).where(Director.id == director_id))
    director = result.scalar_one_or_none()

    if not director:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Director not found"
        )

    # Update fields
    update_data = director_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(director, field, value)

    await db.commit()
    await db.refresh(director)

    # 清除导演缓存
    await Cache.delete_pattern("directors_list:*")

    return DirectorAdminResponse.model_validate(director)


@router.delete("/{director_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_director(
    director_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a director"""
    result = await db.execute(select(Director).where(Director.id == director_id))
    director = result.scalar_one_or_none()

    if not director:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Director not found"
        )

    await db.delete(director)
    await db.commit()

    # 清除导演缓存
    await Cache.delete_pattern("directors_list:*")

    return None
