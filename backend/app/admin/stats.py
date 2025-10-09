from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User, AdminUser
from app.models.video import Video
from app.models.comment import Comment
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


@router.get("/overview")
async def admin_get_overview_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get overview statistics"""
    # Count users
    user_count_result = await db.execute(select(func.count()).select_from(User))
    user_count = user_count_result.scalar()

    # Count videos
    video_count_result = await db.execute(select(func.count()).select_from(Video))
    video_count = video_count_result.scalar()

    # Count comments
    comment_count_result = await db.execute(select(func.count()).select_from(Comment))
    comment_count = comment_count_result.scalar()

    # Total views
    view_count_result = await db.execute(select(func.sum(Video.view_count)))
    total_views = view_count_result.scalar() or 0

    return {
        "total_users": user_count,
        "total_videos": video_count,
        "total_comments": comment_count,
        "total_views": total_views,
    }
