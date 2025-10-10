from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract, and_
from app.database import get_db, get_pool_status
from app.models.user import User, AdminUser
from app.models.video import Video, Category
from app.models.comment import Comment
from app.utils.dependencies import get_current_admin_user
from app.utils.cache import Cache, CacheStats
from app.utils.cache_warmer import CacheWarmer
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/overview")
async def admin_get_overview_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get overview statistics (cached for 5 minutes)"""
    # 尝试从缓存获取
    cache_key = "admin:stats:overview"
    cached = await Cache.get(cache_key)
    if cached is not None:
        return cached

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

    response = {
        "total_users": user_count,
        "total_videos": video_count,
        "total_comments": comment_count,
        "total_views": total_views,
    }

    # 缓存5分钟
    await Cache.set(cache_key, response, ttl=300)

    return response


@router.get("/trends")
async def admin_get_trend_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get trend statistics for the last 30 days (cached for 1 hour)"""
    # 尝试从缓存获取
    cache_key = "admin:stats:trends"
    cached = await Cache.get(cache_key)
    if cached is not None:
        return cached

    # Get data for the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    # User registration trend
    user_trend = await db.execute(
        select(
            func.date(User.created_at).label("date"),
            func.count(User.id).label("count")
        )
        .where(User.created_at >= thirty_days_ago)
        .group_by(func.date(User.created_at))
        .order_by(func.date(User.created_at))
    )
    user_trend_data = [
        {"date": str(row.date), "count": row.count, "type": "新增用户"}
        for row in user_trend.all()
    ]

    # Video upload trend
    video_trend = await db.execute(
        select(
            func.date(Video.created_at).label("date"),
            func.count(Video.id).label("count")
        )
        .where(Video.created_at >= thirty_days_ago)
        .group_by(func.date(Video.created_at))
        .order_by(func.date(Video.created_at))
    )
    video_trend_data = [
        {"date": str(row.date), "count": row.count, "type": "新增视频"}
        for row in video_trend.all()
    ]

    # Comment trend
    comment_trend = await db.execute(
        select(
            func.date(Comment.created_at).label("date"),
            func.count(Comment.id).label("count")
        )
        .where(Comment.created_at >= thirty_days_ago)
        .group_by(func.date(Comment.created_at))
        .order_by(func.date(Comment.created_at))
    )
    comment_trend_data = [
        {"date": str(row.date), "count": row.count, "type": "新增评论"}
        for row in comment_trend.all()
    ]

    response = {
        "user_trend": user_trend_data,
        "video_trend": video_trend_data,
        "comment_trend": comment_trend_data,
        "combined": user_trend_data + video_trend_data + comment_trend_data,
    }

    # 缓存1小时
    await Cache.set(cache_key, response, ttl=3600)

    return response


@router.get("/video-categories")
async def admin_get_video_category_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get video count by category"""
    # This is a simplified version - in production you'd join video_categories table
    result = await db.execute(
        select(Category.name, func.count(Category.id).label("count"))
        .group_by(Category.id, Category.name)
        .order_by(func.count(Category.id).desc())
        .limit(10)
    )

    return [
        {"category": row.name, "count": row.count}
        for row in result.all()
    ]


@router.get("/video-types")
async def admin_get_video_type_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get video count by type"""
    result = await db.execute(
        select(Video.video_type, func.count(Video.id).label("count"))
        .group_by(Video.video_type)
        .order_by(func.count(Video.id).desc())
    )

    type_names = {
        "movie": "电影",
        "tv_series": "电视剧",
        "anime": "动漫",
        "documentary": "纪录片",
    }

    return [
        {"type": type_names.get(row.video_type, row.video_type), "count": row.count}
        for row in result.all()
    ]


@router.get("/top-videos")
async def admin_get_top_videos(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get top 10 videos by views"""
    result = await db.execute(
        select(Video.title, Video.view_count, Video.like_count, Video.comment_count)
        .order_by(Video.view_count.desc())
        .limit(10)
    )

    return [
        {
            "title": row.title,
            "views": row.view_count,
            "likes": row.like_count,
            "comments": row.comment_count,
        }
        for row in result.all()
    ]


@router.get("/database-pool")
async def get_database_pool_status(
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get database connection pool status"""
    return get_pool_status()


@router.get("/cache-stats")
async def get_cache_stats(
    days: int = Query(7, ge=1, le=30),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get cache hit rate statistics"""
    return await CacheStats.get_stats(days=days)


@router.post("/cache-warm")
async def warm_cache(
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Manually trigger cache warming"""
    try:
        await CacheWarmer.warm_all()
        return {"message": "Cache warming completed successfully"}
    except Exception as e:
        return {"message": f"Cache warming failed: {str(e)}", "success": False}
