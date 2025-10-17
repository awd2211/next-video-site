"""
视频分析API - 提供详细的视频观看数据和趋势分析
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, desc, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.comment import Comment
from app.models.user import AdminUser
from app.models.user_activity import Favorite, WatchHistory
from app.models.video import Video
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


@router.get("/videos/{video_id}/analytics")
async def get_video_analytics(
    video_id: int,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取单个视频的详细分析数据

    包括：
    - 基本统计
    - 观看趋势（每日）
    - 完播率分析
    - 观众留存曲线
    - 互动数据（评论、点赞、收藏）
    - 地理分布（如果有）
    """
    # 1. 获取视频基本信息
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # 2. 计算时间范围
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    # 3. 观看趋势（每日观看次数）
    watch_trend_result = await db.execute(
        select(
            func.date(WatchHistory.updated_at).label("date"),
            func.count(WatchHistory.id).label("views"),
            func.count(func.distinct(WatchHistory.user_id)).label("unique_viewers"),
        )
        .filter(
            WatchHistory.video_id == video_id,
            WatchHistory.updated_at >= start_date,
        )
        .group_by(func.date(WatchHistory.updated_at))
        .order_by("date")
    )
    watch_trend = [
        {"date": str(row.date), "views": row.views, "unique_viewers": row.unique_viewers}
        for row in watch_trend_result.fetchall()
    ]

    # 4. 完播率分析
    # Calculate progress as (last_position / video.duration * 100)
    # Get video duration first
    video_duration = video.duration * 60 if video.duration else 1  # convert minutes to seconds

    completion_result = await db.execute(
        select(
            func.count(WatchHistory.id).label("total"),
            func.sum(
                case((WatchHistory.last_position / video_duration * 100 >= 25, 1), else_=0)
            ).label("over_25"),
            func.sum(
                case((WatchHistory.last_position / video_duration * 100 >= 50, 1), else_=0)
            ).label("over_50"),
            func.sum(
                case((WatchHistory.last_position / video_duration * 100 >= 75, 1), else_=0)
            ).label("over_75"),
            func.sum(
                case((WatchHistory.last_position / video_duration * 100 >= 90, 1), else_=0)
            ).label("over_90"),
        ).filter(
            WatchHistory.video_id == video_id,
            WatchHistory.updated_at >= start_date,
        )
    )
    completion_row = completion_result.fetchone()

    completion_rate = {
        "total_views": completion_row.total or 0,
        "0-25%": completion_row.total - (completion_row.over_25 or 0) if completion_row.total else 0,
        "25-50%": (completion_row.over_25 or 0) - (completion_row.over_50 or 0),
        "50-75%": (completion_row.over_50 or 0) - (completion_row.over_75 or 0),
        "75-90%": (completion_row.over_75 or 0) - (completion_row.over_90 or 0),
        "90-100%": completion_row.over_90 or 0,
    }

    # 5. 平均完播率
    avg_progress_result = await db.execute(
        select(func.avg(WatchHistory.last_position / video_duration * 100))
        .filter(
            WatchHistory.video_id == video_id,
            WatchHistory.updated_at >= start_date,
        )
    )
    avg_completion = avg_progress_result.scalar() or 0

    # 6. 评论趋势
    comment_trend_result = await db.execute(
        select(
            func.date(Comment.created_at).label("date"),
            func.count(Comment.id).label("comments"),
        )
        .filter(
            Comment.video_id == video_id,
            Comment.created_at >= start_date,
        )
        .group_by(func.date(Comment.created_at))
        .order_by("date")
    )
    comment_trend = [
        {"date": str(row.date), "comments": row.comments}
        for row in comment_trend_result.fetchall()
    ]

    # 7. 收藏趋势
    favorite_trend_result = await db.execute(
        select(
            func.date(Favorite.created_at).label("date"),
            func.count(Favorite.id).label("favorites"),
        )
        .filter(
            Favorite.video_id == video_id,
            Favorite.created_at >= start_date,
        )
        .group_by(func.date(Favorite.created_at))
        .order_by("date")
    )
    favorite_trend = [
        {"date": str(row.date), "favorites": row.favorites}
        for row in favorite_trend_result.fetchall()
    ]

    # 8. 观看时段分析（小时分布）
    hourly_result = await db.execute(
        select(
            extract("hour", WatchHistory.updated_at).label("hour"),
            func.count(WatchHistory.id).label("views"),
        )
        .filter(
            WatchHistory.video_id == video_id,
            WatchHistory.updated_at >= start_date,
        )
        .group_by("hour")
        .order_by("hour")
    )
    hourly_distribution = [
        {"hour": int(row.hour), "views": row.views} for row in hourly_result.fetchall()
    ]

    # 9. 星期分布
    weekday_result = await db.execute(
        select(
            extract("dow", WatchHistory.updated_at).label("weekday"),
            func.count(WatchHistory.id).label("views"),
        )
        .filter(
            WatchHistory.video_id == video_id,
            WatchHistory.updated_at >= start_date,
        )
        .group_by("weekday")
        .order_by("weekday")
    )
    weekday_names = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
    weekday_distribution = [
        {"weekday": weekday_names[int(row.weekday)], "views": row.views}
        for row in weekday_result.fetchall()
    ]

    # 10. 互动转化率
    total_unique_viewers_result = await db.execute(
        select(func.count(func.distinct(WatchHistory.user_id)))
        .filter(
            WatchHistory.video_id == video_id,
            WatchHistory.updated_at >= start_date,
        )
    )
    total_unique_viewers = total_unique_viewers_result.scalar() or 0

    comment_users_result = await db.execute(
        select(func.count(func.distinct(Comment.user_id)))
        .filter(
            Comment.video_id == video_id,
            Comment.created_at >= start_date,
        )
    )
    comment_users = comment_users_result.scalar() or 0

    favorite_users_result = await db.execute(
        select(func.count(Favorite.id))
        .filter(
            Favorite.video_id == video_id,
            Favorite.created_at >= start_date,
        )
    )
    favorite_users = favorite_users_result.scalar() or 0

    engagement_metrics = {
        "total_unique_viewers": total_unique_viewers,
        "comment_users": comment_users,
        "favorite_users": favorite_users,
        "comment_rate": (comment_users / total_unique_viewers * 100) if total_unique_viewers > 0 else 0,
        "favorite_rate": (favorite_users / total_unique_viewers * 100) if total_unique_viewers > 0 else 0,
    }

    # 返回完整分析结果
    return {
        "video_id": video_id,
        "video_title": video.title,
        "analysis_period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days,
        },
        "basic_stats": {
            "total_views": video.view_count,
            "like_count": video.like_count,
            "favorite_count": video.favorite_count,
            "comment_count": video.comment_count,
            "average_rating": float(video.average_rating),
            "rating_count": video.rating_count,
        },
        "watch_trend": watch_trend,
        "completion_analysis": {
            "completion_rate_distribution": completion_rate,
            "average_completion_percentage": round(float(avg_completion), 2),
        },
        "comment_trend": comment_trend,
        "favorite_trend": favorite_trend,
        "time_distribution": {
            "hourly": hourly_distribution,
            "weekday": weekday_distribution,
        },
        "engagement_metrics": engagement_metrics,
    }


@router.get("/overview/analytics")
async def get_overview_analytics(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取整体视频数据分析概览

    包括：
    - 总体统计
    - 热门视频TOP10
    - 新增视频趋势
    - 整体观看趋势
    """
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    # 1. 总体统计
    total_videos_result = await db.execute(
        select(func.count(Video.id)).filter(Video.status == "published")
    )
    total_videos = total_videos_result.scalar() or 0

    total_views_result = await db.execute(
        select(func.sum(Video.view_count)).filter(Video.status == "published")
    )
    total_views = total_views_result.scalar() or 0

    total_likes_result = await db.execute(
        select(func.sum(Video.like_count)).filter(Video.status == "published")
    )
    total_likes = total_likes_result.scalar() or 0

    # 2. 最近观看趋势
    recent_watch_trend_result = await db.execute(
        select(
            func.date(WatchHistory.updated_at).label("date"),
            func.count(WatchHistory.id).label("views"),
        )
        .filter(WatchHistory.updated_at >= start_date)
        .group_by(func.date(WatchHistory.updated_at))
        .order_by("date")
    )
    watch_trend = [
        {"date": str(row.date), "views": row.views}
        for row in recent_watch_trend_result.fetchall()
    ]

    # 3. 热门视频TOP10
    top_videos_result = await db.execute(
        select(Video)
        .filter(Video.status == "published")
        .order_by(desc(Video.view_count))
        .limit(10)
    )
    top_videos = [
        {
            "id": v.id,
            "title": v.title,
            "view_count": v.view_count,
            "like_count": v.like_count,
            "average_rating": float(v.average_rating),
        }
        for v in top_videos_result.scalars().all()
    ]

    # 4. 新增视频趋势
    new_videos_trend_result = await db.execute(
        select(
            func.date(Video.published_at).label("date"),
            func.count(Video.id).label("count"),
        )
        .filter(Video.published_at >= start_date, Video.status == "published")
        .group_by(func.date(Video.published_at))
        .order_by("date")
    )
    new_videos_trend = [
        {"date": str(row.date), "count": row.count}
        for row in new_videos_trend_result.fetchall()
    ]

    return {
        "analysis_period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days,
        },
        "overall_stats": {
            "total_videos": total_videos,
            "total_views": total_views,
            "total_likes": total_likes,
        },
        "watch_trend": watch_trend,
        "top_videos": top_videos,
        "new_videos_trend": new_videos_trend,
    }


@router.get("/videos/{video_id}/quality-score")
async def get_video_quality_score(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    计算视频质量评分

    评分维度：
    - 技术质量（分辨率、编码格式、文件大小等）
    - 元数据完整度（描述、封面、字幕等）
    - 用户互动（观看数、评分、完播率等）
    """
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Count relationships using SQL queries to avoid lazy loading
    # Import the association models
    from app.models.video import VideoCategory, VideoTag, VideoActor, VideoDirector

    category_count_result = await db.execute(
        select(func.count(VideoCategory.id)).filter(VideoCategory.video_id == video_id)
    )
    category_count = category_count_result.scalar() or 0

    tag_count_result = await db.execute(
        select(func.count(VideoTag.id)).filter(VideoTag.video_id == video_id)
    )
    tag_count = tag_count_result.scalar() or 0

    has_actors_result = await db.execute(
        select(func.count(VideoActor.id)).filter(VideoActor.video_id == video_id)
    )
    has_actors = (has_actors_result.scalar() or 0) > 0

    has_directors_result = await db.execute(
        select(func.count(VideoDirector.id)).filter(VideoDirector.video_id == video_id)
    )
    has_directors = (has_directors_result.scalar() or 0) > 0

    # 1. 技术质量得分 (40分)
    technical_score = 0.0

    # 编码格式（10分）
    if video.is_av1_available:
        technical_score += 10
    elif video.video_url:
        technical_score += 6  # H.264

    # 时长合理性（5分）
    if video.duration:
        if 10 <= video.duration <= 180:  # 10分钟到3小时
            technical_score += 5
        elif video.duration > 0:
            technical_score += 3

    # 文件大小（判断是否有过度压缩或未压缩）（5分）
    if video.h264_file_size:
        size_mb = video.h264_file_size / (1024 * 1024)
        if video.duration and video.duration > 0:
            bitrate = size_mb / video.duration  # MB per minute
            if 10 <= bitrate <= 50:  # 合理比特率范围
                technical_score += 5
            elif bitrate > 0:
                technical_score += 2

    # 转码完成（10分）
    if video.transcode_status == "completed":
        technical_score += 10
    elif video.transcode_status == "processing":
        technical_score += 5

    # 海报/背景图（10分）
    if video.poster_url:
        technical_score += 5
    if video.backdrop_url:
        technical_score += 5

    # 2. 元数据完整度得分 (30分)
    metadata_score = 0.0

    # 标题（必须，5分）
    if video.title:
        metadata_score += 5

    # 描述（10分）
    if video.description:
        desc_len = len(video.description)
        if desc_len >= 100:
            metadata_score += 10
        elif desc_len >= 50:
            metadata_score += 7
        elif desc_len > 0:
            metadata_score += 4

    # 分类（5分）
    if category_count >= 2:
        metadata_score += 5
    elif category_count == 1:
        metadata_score += 3

    # 标签（5分）
    if tag_count >= 3:
        metadata_score += 5
    elif tag_count > 0:
        metadata_score += 3

    # 演员/导演（5分）
    if has_actors or has_directors:
        metadata_score += 5

    # 3. 用户互动得分 (30分)
    engagement_score = 0.0

    # 观看数（10分）
    if video.view_count >= 10000:
        engagement_score += 10
    elif video.view_count >= 1000:
        engagement_score += 7
    elif video.view_count >= 100:
        engagement_score += 5
    elif video.view_count > 0:
        engagement_score += 2

    # 评分（10分）
    if video.rating_count >= 10:
        if video.average_rating >= 8:
            engagement_score += 10
        elif video.average_rating >= 6:
            engagement_score += 7
        elif video.average_rating >= 4:
            engagement_score += 4
        else:
            engagement_score += 2
    elif video.rating_count > 0:
        engagement_score += 3

    # 互动率（10分）- 评论和收藏
    if video.view_count > 0:
        interaction_rate = (video.comment_count + video.favorite_count) / video.view_count
        if interaction_rate >= 0.1:  # 10%互动率
            engagement_score += 10
        elif interaction_rate >= 0.05:  # 5%互动率
            engagement_score += 7
        elif interaction_rate >= 0.01:  # 1%互动率
            engagement_score += 4
        elif interaction_rate > 0:
            engagement_score += 2

    # 总分
    total_score = technical_score + metadata_score + engagement_score

    # 评级
    if total_score >= 90:
        grade = "S"
        grade_text = "优秀"
    elif total_score >= 80:
        grade = "A"
        grade_text = "良好"
    elif total_score >= 70:
        grade = "B"
        grade_text = "中等"
    elif total_score >= 60:
        grade = "C"
        grade_text = "及格"
    else:
        grade = "D"
        grade_text = "待改进"

    # 生成改进建议
    suggestions = []
    if technical_score < 30:
        if not video.is_av1_available:
            suggestions.append(
                {"issue": "encoding", "message": "建议启用AV1编码以提升质量", "potential_gain": "+10分"}
            )
        if not video.poster_url:
            suggestions.append(
                {"issue": "poster", "message": "添加视频封面图", "potential_gain": "+5分"}
            )

    if metadata_score < 20:
        if not video.description or len(video.description) < 100:
            suggestions.append(
                {"issue": "description", "message": "添加详细的视频描述（至少100字）", "potential_gain": "+10分"}
            )
        if category_count < 2:
            suggestions.append(
                {"issue": "categories", "message": "添加更多相关分类", "potential_gain": "+5分"}
            )

    if engagement_score < 15:
        suggestions.append(
            {"issue": "promotion", "message": "增加视频推广，提升观看量和互动", "potential_gain": "+20分"}
        )

    return {
        "video_id": video_id,
        "video_title": video.title,
        "quality_score": {
            "total": round(total_score, 2),
            "grade": grade,
            "grade_text": grade_text,
            "breakdown": {
                "technical": round(technical_score, 2),
                "metadata": round(metadata_score, 2),
                "engagement": round(engagement_score, 2),
            },
        },
        "suggestions": suggestions,
    }
