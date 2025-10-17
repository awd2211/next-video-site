"""
报表生成系统 API
支持用户活动、内容表现、VIP订阅等多种报表
支持导出 Excel 和 PDF 格式
"""

from datetime import datetime, timedelta, timezone
from io import BytesIO

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from loguru import logger
from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.comment import Comment
from app.models.user import AdminUser, User
from app.models.user_activity import Favorite, WatchHistory
from app.models.video import Video
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


# ========== 用户活动报表 ==========


@router.get("/user-activity")
async def get_user_activity_report(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    用户活动报表
    包含：新增用户趋势、活跃用户、用户行为统计等
    """
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    end_date = datetime.now(timezone.utc)

    # 1. 新增用户趋势（按天）
    user_trend_result = await db.execute(
        select(
            func.date(User.created_at).label("date"),
            func.count(User.id).label("count"),
        )
        .where(User.created_at >= start_date)
        .group_by(func.date(User.created_at))
        .order_by(func.date(User.created_at))
    )
    user_trend = [{"date": str(row.date), "count": row.count} for row in user_trend_result]

    # 2. 总体统计
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar()

    new_users_result = await db.execute(
        select(func.count(User.id)).where(User.created_at >= start_date)
    )
    new_users = new_users_result.scalar()

    # 3. 活跃用户（在时间范围内有观看记录）
    active_users_result = await db.execute(
        select(func.count(func.distinct(WatchHistory.user_id))).where(
            WatchHistory.updated_at >= start_date
        )
    )
    active_users = active_users_result.scalar()

    # 4. VIP 用户统计
    vip_users_result = await db.execute(
        select(func.count(User.id)).where(
            User.is_vip == True, or_(User.vip_expires_at == None, User.vip_expires_at > end_date)
        )
    )
    vip_users = vip_users_result.scalar()

    # 5. 用户行为统计
    watch_count_result = await db.execute(
        select(func.count(WatchHistory.id)).where(WatchHistory.updated_at >= start_date)
    )
    total_watches = watch_count_result.scalar()

    comment_count_result = await db.execute(
        select(func.count(Comment.id)).where(Comment.created_at >= start_date)
    )
    total_comments = comment_count_result.scalar()

    favorite_count_result = await db.execute(
        select(func.count(Favorite.id)).where(Favorite.created_at >= start_date)
    )
    total_favorites = favorite_count_result.scalar()

    logger.info(f"管理员 {current_admin.username} 生成了用户活动报表（{days}天）")

    return {
        "report_type": "user_activity",
        "period": {"start": start_date, "end": end_date, "days": days},
        "summary": {
            "total_users": total_users,
            "new_users": new_users,
            "active_users": active_users,
            "vip_users": vip_users,
            "active_rate": round(active_users / total_users * 100, 2) if total_users > 0 else 0,
        },
        "user_trend": user_trend,
        "behavior_stats": {
            "total_watches": total_watches,
            "total_comments": total_comments,
            "total_favorites": total_favorites,
            "avg_watches_per_user": round(total_watches / active_users, 2)
            if active_users > 0
            else 0,
        },
    }


# ========== 内容表现报表 ==========


@router.get("/content-performance")
async def get_content_performance_report(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    limit: int = Query(20, ge=5, le=100, description="TOP N"),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    内容表现报表
    包含：热门视频、新增视频趋势、分类分布等
    """
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    # 1. 新增视频趋势
    video_trend_result = await db.execute(
        select(
            func.date(Video.created_at).label("date"),
            func.count(Video.id).label("count"),
        )
        .where(Video.created_at >= start_date)
        .group_by(func.date(Video.created_at))
        .order_by(func.date(Video.created_at))
    )
    video_trend = [{"date": str(row.date), "count": row.count} for row in video_trend_result]

    # 2. 总体统计
    total_videos_result = await db.execute(select(func.count(Video.id)))
    total_videos = total_videos_result.scalar()

    new_videos_result = await db.execute(
        select(func.count(Video.id)).where(Video.created_at >= start_date)
    )
    new_videos = new_videos_result.scalar()

    # 3. 热门视频 TOP N（按观看数排序）
    top_videos_result = await db.execute(
        select(Video)
        .where(Video.created_at >= start_date)
        .order_by(Video.view_count.desc())
        .limit(limit)
    )
    top_videos = [
        {
            "id": v.id,
            "title": v.title,
            "video_type": v.video_type.value if v.video_type else None,
            "views": v.view_count,
            "likes": v.like_count,
            "favorites": v.favorite_count,
            "comments": v.comment_count,
            "rating": float(v.average_rating) if v.average_rating else 0,
            "created_at": v.created_at,
        }
        for v in top_videos_result.scalars()
    ]

    # 4. 视频类型分布
    type_distribution_result = await db.execute(
        select(Video.video_type, func.count(Video.id).label("count"))
        .group_by(Video.video_type)
        .order_by(func.count(Video.id).desc())
    )
    type_distribution = [
        {"type": row.video_type.value if row.video_type else "unknown", "count": row.count}
        for row in type_distribution_result
    ]

    # 5. 总观看数和互动数
    total_views_result = await db.execute(select(func.sum(Video.view_count)))
    total_views = total_views_result.scalar() or 0

    total_likes_result = await db.execute(select(func.sum(Video.like_count)))
    total_likes = total_likes_result.scalar() or 0

    logger.info(f"管理员 {current_admin.username} 生成了内容表现报表（{days}天，TOP{limit}）")

    return {
        "report_type": "content_performance",
        "period": {"start": start_date, "end": datetime.now(timezone.utc), "days": days},
        "summary": {
            "total_videos": total_videos,
            "new_videos": new_videos,
            "total_views": total_views,
            "total_likes": total_likes,
            "avg_views_per_video": round(total_views / total_videos, 2)
            if total_videos > 0
            else 0,
        },
        "video_trend": video_trend,
        "top_videos": top_videos,
        "type_distribution": type_distribution,
    }


# ========== VIP订阅报表 ==========


@router.get("/vip-subscription")
async def get_vip_subscription_report(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    VIP订阅报表
    包含：VIP用户数、续费率、到期分析等
    """
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    now = datetime.now(timezone.utc)

    # 1. 当前 VIP 用户总数
    total_vip_result = await db.execute(
        select(func.count(User.id)).where(
            User.is_vip == True, or_(User.vip_expires_at == None, User.vip_expires_at > now)
        )
    )
    total_vip = total_vip_result.scalar()

    # 2. 新增 VIP（假设通过创建时间和 is_vip 判断）
    # 注意：这里简化处理，实际应该有专门的订阅记录表
    new_vip_result = await db.execute(
        select(func.count(User.id)).where(
            User.is_vip == True, User.created_at >= start_date
        )
    )
    new_vip = new_vip_result.scalar()

    # 3. 即将到期的 VIP（未来7天）
    expire_soon_date = now + timedelta(days=7)
    expiring_vip_result = await db.execute(
        select(func.count(User.id)).where(
            User.is_vip == True,
            User.vip_expires_at != None,
            User.vip_expires_at > now,
            User.vip_expires_at <= expire_soon_date,
        )
    )
    expiring_vip = expiring_vip_result.scalar()

    # 4. 已过期 VIP（最近30天）
    expired_vip_result = await db.execute(
        select(func.count(User.id)).where(
            User.vip_expires_at != None,
            User.vip_expires_at <= now,
            User.vip_expires_at >= start_date,
        )
    )
    expired_vip = expired_vip_result.scalar()

    logger.info(f"管理员 {current_admin.username} 生成了VIP订阅报表（{days}天）")

    return {
        "report_type": "vip_subscription",
        "period": {"start": start_date, "end": now, "days": days},
        "summary": {
            "total_vip": total_vip,
            "new_vip": new_vip,
            "expiring_soon": expiring_vip,
            "expired": expired_vip,
        },
        "alerts": [
            f"{expiring_vip} 个用户的VIP即将在7天内到期" if expiring_vip > 0 else None,
            f"{expired_vip} 个用户的VIP在最近{days}天内已过期" if expired_vip > 0 else None,
        ],
    }


# ========== 导出 Excel 报表 ==========


@router.get("/export/excel")
async def export_excel_report(
    report_type: str = Query(
        ..., regex="^(user-activity|content-performance|vip-subscription)$"
    ),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    导出 Excel 格式的报表
    需要安装: pip install pandas openpyxl
    """
    try:
        import pandas as pd
    except ImportError:
        return {"error": "需要安装 pandas 和 openpyxl: pip install pandas openpyxl"}

    # 获取报表数据
    if report_type == "user-activity":
        data = await get_user_activity_report(days, db, current_admin)
        df_trend = pd.DataFrame(data["user_trend"])
        df_summary = pd.DataFrame([data["summary"]])

        # 创建 Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_summary.to_excel(writer, sheet_name="总体统计", index=False)
            df_trend.to_excel(writer, sheet_name="用户增长趋势", index=False)

    elif report_type == "content-performance":
        data = await get_content_performance_report(days, 20, db, current_admin)
        df_summary = pd.DataFrame([data["summary"]])
        df_top_videos = pd.DataFrame(data["top_videos"])
        df_type = pd.DataFrame(data["type_distribution"])

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_summary.to_excel(writer, sheet_name="总体统计", index=False)
            df_top_videos.to_excel(writer, sheet_name="热门视频TOP20", index=False)
            df_type.to_excel(writer, sheet_name="视频类型分布", index=False)

    elif report_type == "vip-subscription":
        data = await get_vip_subscription_report(days, db, current_admin)
        df_summary = pd.DataFrame([data["summary"]])

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_summary.to_excel(writer, sheet_name="VIP统计", index=False)

    output.seek(0)
    filename = f"{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    logger.info(f"管理员 {current_admin.username} 导出了 {report_type} Excel 报表")

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ========== 获取所有报表类型 ==========


@router.get("/types")
async def get_report_types(
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取所有可用的报表类型"""
    return {
        "report_types": [
            {
                "type": "user-activity",
                "name": "用户活动报表",
                "description": "统计用户注册、活跃度、行为等数据",
                "icon": "UserOutlined",
            },
            {
                "type": "content-performance",
                "name": "内容表现报表",
                "description": "统计视频发布、观看、互动等数据",
                "icon": "VideoCameraOutlined",
            },
            {
                "type": "vip-subscription",
                "name": "VIP订阅报表",
                "description": "统计VIP用户数、续费、到期等数据",
                "icon": "CrownOutlined",
            },
        ]
    }
