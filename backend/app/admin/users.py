from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import AdminUser, User
from app.models.comment import Comment, Rating
from app.models.user_activity import WatchHistory, Favorite
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

    username = user.username or user.email
    user.is_active = False
    await db.commit()

    # 🆕 发送封禁通知
    try:
        from app.utils.admin_notification_service import AdminNotificationService

        await AdminNotificationService.notify_user_banned(
            db=db,
            user_id=user_id,
            username=username,
            action="banned",
            admin_username=current_admin.username,
        )
    except Exception as e:
        print(f"Failed to send user ban notification: {e}")

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

    username = user.username or user.email
    user.is_active = True
    await db.commit()

    # 🆕 发送解封通知
    try:
        from app.utils.admin_notification_service import AdminNotificationService

        await AdminNotificationService.notify_user_banned(
            db=db,
            user_id=user_id,
            username=username,
            action="unbanned",
            admin_username=current_admin.username,
        )
    except Exception as e:
        print(f"Failed to send user unban notification: {e}")

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

    # 🆕 发送批量封禁通知
    if users:
        try:
            from app.utils.admin_notification_service import AdminNotificationService

            await AdminNotificationService.notify_user_banned(
                db=db,
                user_id=users[0].id,
                username="",
                action="banned",
                admin_username=current_admin.username,
                user_count=len(users),
            )
        except Exception as e:
            print(f"Failed to send batch ban notification: {e}")

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

    # 🆕 发送批量解封通知
    if users:
        try:
            from app.utils.admin_notification_service import AdminNotificationService

            await AdminNotificationService.notify_user_banned(
                db=db,
                user_id=users[0].id,
                username="",
                action="unbanned",
                admin_username=current_admin.username,
                user_count=len(users),
            )
        except Exception as e:
            print(f"Failed to send batch unban notification: {e}")

    return {"message": f"Successfully unbanned {len(users)} users", "count": len(users)}


@router.get("/{user_id}/detail")
async def admin_get_user_detail(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    Admin: Get detailed user information

    Returns:
    - User basic info
    - Activity statistics
    - Recent watch history
    - Recent comments
    - Favorite videos
    - VIP information
    """
    # Get user
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get activity statistics
    # Watch history count
    watch_count_result = await db.execute(
        select(func.count(WatchHistory.id)).where(WatchHistory.user_id == user_id)
    )
    total_watch_count = watch_count_result.scalar() or 0

    # Favorite count
    favorite_count_result = await db.execute(
        select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
    )
    total_favorites = favorite_count_result.scalar() or 0

    # Comment count
    comment_count_result = await db.execute(
        select(func.count(Comment.id)).where(Comment.user_id == user_id)
    )
    total_comments = comment_count_result.scalar() or 0

    # Rating count
    rating_count_result = await db.execute(
        select(func.count(Rating.id)).where(Rating.user_id == user_id)
    )
    total_ratings = rating_count_result.scalar() or 0

    # Get recent watch history (last 20)
    watch_history_result = await db.execute(
        select(WatchHistory)
        .options(selectinload(WatchHistory.video))
        .where(WatchHistory.user_id == user_id)
        .order_by(desc(WatchHistory.updated_at))
        .limit(20)
    )
    recent_watches = watch_history_result.scalars().all()

    # Get recent comments (last 20)
    comments_result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.video))
        .where(Comment.user_id == user_id)
        .order_by(desc(Comment.created_at))
        .limit(20)
    )
    recent_comments = comments_result.scalars().all()

    # Get favorite videos (last 20)
    favorites_result = await db.execute(
        select(Favorite)
        .options(selectinload(Favorite.video))
        .where(Favorite.user_id == user_id)
        .order_by(desc(Favorite.created_at))
        .limit(20)
    )
    recent_favorites = favorites_result.scalars().all()

    # Calculate activity in last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    recent_watch_result = await db.execute(
        select(func.count(WatchHistory.id))
        .where(WatchHistory.user_id == user_id, WatchHistory.updated_at >= seven_days_ago)
    )
    recent_watches_7d = recent_watch_result.scalar() or 0

    recent_comment_result = await db.execute(
        select(func.count(Comment.id))
        .where(Comment.user_id == user_id, Comment.created_at >= seven_days_ago)
    )
    recent_comments_7d = recent_comment_result.scalar() or 0

    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "avatar": user.avatar,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "is_vip": user.is_vip,
            "vip_expires_at": user.vip_expires_at.isoformat() if user.vip_expires_at else None,
            "created_at": user.created_at.isoformat(),
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        },
        "statistics": {
            "total_watch_count": total_watch_count,
            "total_favorites": total_favorites,
            "total_comments": total_comments,
            "total_ratings": total_ratings,
            "recent_watches_7d": recent_watches_7d,
            "recent_comments_7d": recent_comments_7d,
        },
        "recent_activity": {
            "watch_history": [
                {
                    "id": wh.id,
                    "video": {
                        "id": wh.video.id if wh.video else None,
                        "title": wh.video.title if wh.video else None,
                        "cover_url": wh.video.cover_url if wh.video else None,
                    } if wh.video else None,
                    "progress": wh.progress,
                    "duration": wh.duration,
                    "completed": wh.completed,
                    "updated_at": wh.updated_at.isoformat(),
                }
                for wh in recent_watches
            ],
            "comments": [
                {
                    "id": c.id,
                    "video": {
                        "id": c.video.id if c.video else None,
                        "title": c.video.title if c.video else None,
                    } if c.video else None,
                    "content": c.content,
                    "status": c.status,
                    "created_at": c.created_at.isoformat(),
                }
                for c in recent_comments
            ],
            "favorites": [
                {
                    "id": f.id,
                    "video": {
                        "id": f.video.id if f.video else None,
                        "title": f.video.title if f.video else None,
                        "cover_url": f.video.cover_url if f.video else None,
                    } if f.video else None,
                    "created_at": f.created_at.isoformat(),
                }
                for f in recent_favorites
            ],
        }
    }
