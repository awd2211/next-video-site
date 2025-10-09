from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.video import Category
from app.schemas.video import CategoryResponse

router = APIRouter()


@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
):
    """Get all active categories"""
    result = await db.execute(
        select(Category).filter(Category.is_active == True).order_by(Category.sort_order)
    )
    categories = result.scalars().all()
    return categories
