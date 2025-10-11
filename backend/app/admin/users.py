from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import AdminUser, User
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


@router.get("")
async def admin_list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get all users"""
    query = select(User)
    count_result = await db.execute(select(func.count()).select_from(User))
    total = count_result.scalar() or 0

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()

    return {"total": total, "page": page, "page_size": page_size, "items": users}


@router.put("/{user_id}/ban")
async def admin_ban_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Ban user"""
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    await db.commit()
    return {"message": "User banned successfully"}
