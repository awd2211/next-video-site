from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import csv
import io

from app.database import get_db
from app.models.user import AdminUser, User
from app.models.comment import Comment, Rating
from app.models.user_activity import WatchHistory, Favorite
from app.utils.dependencies import get_current_admin_user
from app.utils.sorting import apply_sorting, normalize_sort_field

router = APIRouter()


class BatchUserOperation(BaseModel):
    """批量用户操作请求体"""

    ids: list[int]


class UpdateVIPRequest(BaseModel):
    """更新VIP请求体"""

    is_vip: bool
    vip_expires_at: Optional[str] = None


@router.get("")
async def admin_list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by username or email"),
    status: Optional[str] = Query(
        None, description="Filter by status: active, banned, all"
    ),
    is_vip: Optional[bool] = Query(None, description="Filter by VIP status"),
    sort_by: Optional[str] = Query(
        "created_at",
        description="排序字段: id, username, email, created_at, last_login_at, is_active, is_vip",
    ),
    sort_order: Optional[str] = Query(
        "desc", regex="^(asc|desc)$", description="排序顺序: asc (升序) 或 desc (降序)"
    ),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get all users with search and filters"""
    query = select(User)

    # Apply search filter
    if search:
        search_filter = or_(
            User.username.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%"),
            User.full_name.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    # Apply status filter
    if status == "active":
        query = query.where(User.is_active == True)
    elif status == "banned":
        query = query.where(User.is_active == False)

    # Apply VIP filter
    if is_vip is not None:
        query = query.where(User.is_vip == is_vip)

    # Count total with filters
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Apply sorting
    sort_field = normalize_sort_field(sort_by)
    allowed_sort_fields = [
        "id",
        "username",
        "email",
        "full_name",
        "created_at",
        "updated_at",
        "last_login_at",
        "is_active",
        "is_vip",
        "is_verified",
    ]
    query = apply_sorting(
        query,
        User,
        sort_field,
        sort_order,
        default_sort="created_at",
        allowed_fields=allowed_sort_fields,
    )

    # Apply pagination
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


@router.put("/batch/ban")
async def admin_batch_ban_users(
    request: BatchUserOperation,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Batch ban users"""
    if not request.ids:
        raise HTTPException(status_code=400, detail="No user IDs provided")

    result = await db.execute(select(User).filter(User.id.in_(request.ids)))
    users = result.scalars().all()

    if not users:
        raise HTTPException(status_code=404, detail="No users found")

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


@router.put("/batch/unban")
async def admin_batch_unban_users(
    request: BatchUserOperation,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Batch unban users"""
    if not request.ids:
        raise HTTPException(status_code=400, detail="No user IDs provided")

    result = await db.execute(select(User).filter(User.id.in_(request.ids)))
    users = result.scalars().all()

    if not users:
        raise HTTPException(status_code=404, detail="No users found")

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


@router.put("/{user_id}/vip")
async def admin_update_user_vip(
    user_id: int,
    request: UpdateVIPRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Update user VIP status"""
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_vip = request.is_vip
    if request.vip_expires_at:
        user.vip_expires_at = datetime.fromisoformat(
            request.vip_expires_at.replace("Z", "+00:00")
        )
    elif not request.is_vip:
        user.vip_expires_at = None

    await db.commit()

    return {
        "message": "VIP status updated successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "is_vip": user.is_vip,
            "vip_expires_at": (
                user.vip_expires_at.isoformat() if user.vip_expires_at else None
            ),
        },
    }


@router.get("/export")
async def admin_export_users(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    is_vip: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Export users to CSV"""
    query = select(User)

    # Apply same filters as list endpoint
    if search:
        search_filter = or_(
            User.username.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%"),
            User.full_name.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    if status == "active":
        query = query.where(User.is_active == True)
    elif status == "banned":
        query = query.where(User.is_active == False)

    if is_vip is not None:
        query = query.where(User.is_vip == is_vip)

    # Get all users (limit to 10000 for safety)
    query = query.order_by(desc(User.created_at)).limit(10000)
    result = await db.execute(query)
    users = result.scalars().all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(
        [
            "ID",
            "Username",
            "Email",
            "Full Name",
            "Status",
            "VIP",
            "VIP Expires At",
            "Verified",
            "Created At",
            "Last Login",
        ]
    )

    # Write data
    for user in users:
        writer.writerow(
            [
                user.id,
                user.username,
                user.email,
                user.full_name or "",
                "Active" if user.is_active else "Banned",
                "Yes" if user.is_vip else "No",
                user.vip_expires_at.isoformat() if user.vip_expires_at else "",
                "Yes" if user.is_verified else "No",
                user.created_at.isoformat(),
                user.last_login_at.isoformat() if user.last_login_at else "",
            ]
        )

    # Prepare response
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        },
    )


@router.put("/batch/vip")
async def admin_batch_update_vip(
    request: BatchUserOperation,
    is_vip: bool = Query(..., description="Grant or remove VIP"),
    vip_expires_at: Optional[str] = Query(
        None, description="VIP expiry date (ISO format)"
    ),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Batch update user VIP status"""
    if not request.ids:
        raise HTTPException(status_code=400, detail="No user IDs provided")

    result = await db.execute(select(User).filter(User.id.in_(request.ids)))
    users = result.scalars().all()

    if not users:
        raise HTTPException(status_code=404, detail="No users found")

    # Update VIP status for all users
    for user in users:
        user.is_vip = is_vip
        if is_vip and vip_expires_at:
            user.vip_expires_at = datetime.fromisoformat(
                vip_expires_at.replace("Z", "+00:00")
            )
        elif not is_vip:
            user.vip_expires_at = None

    await db.commit()

    action = "granted" if is_vip else "removed"
    return {
        "message": f"Successfully {action} VIP for {len(users)} users",
        "count": len(users),
        "is_vip": is_vip,
    }


@router.get("/{user_id}/detail")
async def admin_get_user_detail(
    user_id: int,
    days: int = Query(7, ge=1, le=365, description="Days for recent activity stats"),
    limit: int = Query(20, ge=1, le=100, description="Limit for recent activities"),
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

    # Calculate time range
    time_ago = datetime.utcnow() - timedelta(days=days)

    # Get activity statistics (use parallel queries for better performance)
    stats_queries = [
        select(func.count(WatchHistory.id)).where(WatchHistory.user_id == user_id),
        select(func.count(Favorite.id)).where(Favorite.user_id == user_id),
        select(func.count(Comment.id)).where(Comment.user_id == user_id),
        select(func.count(Rating.id)).where(Rating.user_id == user_id),
        select(func.count(WatchHistory.id)).where(
            WatchHistory.user_id == user_id, WatchHistory.updated_at >= time_ago
        ),
        select(func.count(Comment.id)).where(
            Comment.user_id == user_id, Comment.created_at >= time_ago
        ),
    ]

    # Execute all stats queries
    stats_results = []
    for query in stats_queries:
        result = await db.execute(query)
        stats_results.append(result.scalar() or 0)

    (
        total_watch_count,
        total_favorites,
        total_comments,
        total_ratings,
        recent_watches_count,
        recent_comments_count,
    ) = stats_results

    # Get recent watch history with video info using JOIN instead of selectinload
    from app.models.video import Video

    watch_history_query = (
        select(WatchHistory, Video)
        .outerjoin(Video, WatchHistory.video_id == Video.id)
        .where(WatchHistory.user_id == user_id)
        .order_by(desc(WatchHistory.updated_at))
        .limit(limit)
    )
    watch_history_result = await db.execute(watch_history_query)
    watch_history_rows = watch_history_result.all()

    # Get recent comments with video info using JOIN
    comments_query = (
        select(Comment, Video)
        .outerjoin(Video, Comment.video_id == Video.id)
        .where(Comment.user_id == user_id)
        .order_by(desc(Comment.created_at))
        .limit(limit)
    )
    comments_result = await db.execute(comments_query)
    comments_rows = comments_result.all()

    # Get favorite videos using JOIN
    favorites_query = (
        select(Favorite, Video)
        .outerjoin(Video, Favorite.video_id == Video.id)
        .where(Favorite.user_id == user_id)
        .order_by(desc(Favorite.created_at))
        .limit(limit)
    )
    favorites_result = await db.execute(favorites_query)
    favorites_rows = favorites_result.all()

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
            "vip_expires_at": (
                user.vip_expires_at.isoformat() if user.vip_expires_at else None
            ),
            "created_at": user.created_at.isoformat(),
            "last_login_at": (
                user.last_login_at.isoformat() if user.last_login_at else None
            ),
        },
        "statistics": {
            "total_watch_count": total_watch_count,
            "total_favorites": total_favorites,
            "total_comments": total_comments,
            "total_ratings": total_ratings,
            "recent_watches": recent_watches_count,
            "recent_comments": recent_comments_count,
            "days": days,
        },
        "recent_activity": {
            "watch_history": [
                {
                    "id": wh.id,
                    "video": (
                        {
                            "id": video.id,
                            "title": video.title,
                            "cover_url": video.cover_url,
                        }
                        if video
                        else None
                    ),
                    "last_position": wh.last_position,
                    "completed": wh.completed,
                    "updated_at": wh.updated_at.isoformat(),
                }
                for wh, video in watch_history_rows
            ],
            "comments": [
                {
                    "id": comment.id,
                    "video": (
                        {
                            "id": video.id,
                            "title": video.title,
                        }
                        if video
                        else None
                    ),
                    "content": comment.content,
                    "status": comment.status,
                    "created_at": comment.created_at.isoformat(),
                }
                for comment, video in comments_rows
            ],
            "favorites": [
                {
                    "id": fav.id,
                    "video": (
                        {
                            "id": video.id,
                            "title": video.title,
                            "cover_url": video.cover_url,
                        }
                        if video
                        else None
                    ),
                    "created_at": fav.created_at.isoformat(),
                }
                for fav, video in favorites_rows
            ],
        },
    }
