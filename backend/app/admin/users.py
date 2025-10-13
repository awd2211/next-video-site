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


@router.get("/stats")
async def admin_get_user_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get user statistics"""
    # Total users
    total_result = await db.execute(select(func.count(User.id)))
    total_users = total_result.scalar() or 0

    # Active users
    active_result = await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    active_users = active_result.scalar() or 0

    # Banned users
    banned_users = total_users - active_users

    # VIP users
    vip_result = await db.execute(
        select(func.count(User.id)).where(User.is_vip == True)
    )
    vip_users = vip_result.scalar() or 0

    # Verified users
    verified_result = await db.execute(
        select(func.count(User.id)).where(User.is_verified == True)
    )
    verified_users = verified_result.scalar() or 0

    return {
        "total_users": total_users,
        "active_users": active_users,
        "banned_users": banned_users,
        "vip_users": vip_users,
        "verified_users": verified_users,
    }


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

@router.put("/{user_id}/unban")
async def admin_unban_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Unban user"""
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    await db.commit()
    return {"message": "User unbanned successfully"}


@router.post("/batch/ban")
async def admin_batch_ban_users(
    user_ids: list[int],
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Batch ban users"""
    result = await db.execute(select(User).filter(User.id.in_(user_ids)))
    users = result.scalars().all()

    for user in users:
        user.is_active = False

    await db.commit()
    return {"message": f"Successfully banned {len(users)} users", "count": len(users)}


@router.post("/batch/unban")
async def admin_batch_unban_users(
    user_ids: list[int],
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Batch unban users"""
    result = await db.execute(select(User).filter(User.id.in_(user_ids)))
    users = result.scalars().all()

    for user in users:
        user.is_active = True

    await db.commit()
    return {"message": f"Successfully unbanned {len(users)} users", "count": len(users)}
