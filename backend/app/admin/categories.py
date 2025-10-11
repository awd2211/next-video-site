import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import AdminUser
from app.models.video import Category
from app.schemas.admin_content import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    PaginatedCategoryResponse,
)
from app.utils.cache import Cache
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


@router.get("/", response_model=PaginatedCategoryResponse)
async def get_categories(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", description="Search categories by name"),
    is_active: bool = Query(None, description="Filter by active status"),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all categories with pagination and search"""
    query = select(Category)

    if search:
        query = query.where(Category.name.ilike(f"%{search}%"))

    if is_active is not None:
        query = query.where(Category.is_active == is_active)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    query = (
        query.order_by(Category.sort_order, Category.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    categories = result.scalars().all()

    items = [CategoryResponse.model_validate(cat) for cat in categories]

    return PaginatedCategoryResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if page_size > 0 and total > 0 else 0,
        items=items,
    )


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new category"""
    # Check if category name already exists
    existing_name = await db.execute(
        select(Category).where(Category.name == category_data.name)
    )
    if existing_name.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name already exists",
        )

    # Check if slug already exists
    existing_slug = await db.execute(
        select(Category).where(Category.slug == category_data.slug)
    )
    if existing_slug.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category slug already exists",
        )

    # Verify parent category exists if provided
    if category_data.parent_id:
        parent_result = await db.execute(
            select(Category).where(Category.id == category_data.parent_id)
        )
        if not parent_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found",
            )

    # Create category
    category = Category(**category_data.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)

    # 清除分类缓存
    await Cache.delete_pattern("categories:*")

    return CategoryResponse.model_validate(category)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get category by ID"""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    return CategoryResponse.model_validate(category)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a category"""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    # Check for duplicate name
    if category_data.name and category_data.name != category.name:
        existing = await db.execute(
            select(Category).where(Category.name == category_data.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists",
            )

    # Check for duplicate slug
    if category_data.slug and category_data.slug != category.slug:
        existing = await db.execute(
            select(Category).where(Category.slug == category_data.slug)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category slug already exists",
            )

    # Verify parent category exists if provided
    if category_data.parent_id:
        # Prevent self-referencing
        if category_data.parent_id == category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category cannot be its own parent",
            )

        parent_result = await db.execute(
            select(Category).where(Category.id == category_data.parent_id)
        )
        if not parent_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found",
            )

    # Update fields
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)

    # 清除分类缓存
    await Cache.delete_pattern("categories:*")

    return CategoryResponse.model_validate(category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a category"""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    # Check for child categories
    children_result = await db.execute(
        select(func.count()).where(Category.parent_id == category_id)
    )
    children_count = children_result.scalar() or 0

    if children_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category with {children_count} child categories",
        )

    await db.delete(category)
    await db.commit()

    # 清除分类缓存
    await Cache.delete_pattern("categories:*")

    return None
