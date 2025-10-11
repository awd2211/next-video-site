from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import AdminUser
from app.models.video import Country
from app.schemas.admin_content import (
    CountryCreate,
    CountryResponse,
    CountryUpdate,
    PaginatedCountryResponse,
)
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


@router.get("/", response_model=PaginatedCountryResponse)
async def get_countries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", description="Search countries by name"),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all countries with pagination and search"""
    query = select(Country)

    if search:
        query = query.where(Country.name.ilike(f"%{search}%"))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.order_by(Country.name).offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    countries = result.scalars().all()

    items = [CountryResponse.model_validate(country) for country in countries]

    return PaginatedCountryResponse(
        total=total, page=page, page_size=page_size, items=items
    )


@router.post("/", response_model=CountryResponse, status_code=status.HTTP_201_CREATED)
async def create_country(
    country_data: CountryCreate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new country"""
    # Check if country name already exists
    existing_name = await db.execute(
        select(Country).where(Country.name == country_data.name)
    )
    if existing_name.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Country name already exists",
        )

    # Check if code already exists
    existing_code = await db.execute(
        select(Country).where(Country.code == country_data.code)
    )
    if existing_code.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Country code already exists",
        )

    # Create country
    country = Country(**country_data.model_dump())
    db.add(country)
    await db.commit()
    await db.refresh(country)

    return CountryResponse.model_validate(country)


@router.get("/{country_id}", response_model=CountryResponse)
async def get_country(
    country_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get country by ID"""
    result = await db.execute(select(Country).where(Country.id == country_id))
    country = result.scalar_one_or_none()

    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Country not found"
        )

    return CountryResponse.model_validate(country)


@router.put("/{country_id}", response_model=CountryResponse)
async def update_country(
    country_id: int,
    country_data: CountryUpdate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a country"""
    result = await db.execute(select(Country).where(Country.id == country_id))
    country = result.scalar_one_or_none()

    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Country not found"
        )

    # Check for duplicate name
    if country_data.name and country_data.name != country.name:
        existing = await db.execute(
            select(Country).where(Country.name == country_data.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Country name already exists",
            )

    # Check for duplicate code
    if country_data.code and country_data.code != country.code:
        existing = await db.execute(
            select(Country).where(Country.code == country_data.code)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Country code already exists",
            )

    # Update fields
    update_data = country_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(country, field, value)

    await db.commit()
    await db.refresh(country)

    return CountryResponse.model_validate(country)


@router.delete("/{country_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_country(
    country_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a country"""
    result = await db.execute(select(Country).where(Country.id == country_id))
    country = result.scalar_one_or_none()

    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Country not found"
        )

    await db.delete(country)
    await db.commit()

    return None
