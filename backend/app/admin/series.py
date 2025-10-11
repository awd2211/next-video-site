"""
视频专辑/系列管理 - 管理员API
"""

import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.series import Series, SeriesStatus, SeriesType, series_videos
from app.models.user import AdminUser
from app.models.video import Video
from app.schemas.series import (
    PaginatedSeriesResponse,
    SeriesAddVideos,
    SeriesCreate,
    SeriesDetailResponse,
    SeriesListResponse,
    SeriesRemoveVideos,
    SeriesUpdate,
    SeriesUpdateVideoOrder,
    SeriesVideoItem,
)
from app.utils.cache import Cache
from app.utils.dependencies import get_current_admin_user
from app.utils.rate_limit import RateLimitPresets, limiter

router = APIRouter()


@router.get(
    "", response_model=PaginatedSeriesResponse, summary="获取专辑列表（管理员）"
)
@limiter.limit(RateLimitPresets.ADMIN_READ)
async def admin_get_series_list(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[SeriesStatus] = Query(None, description="状态筛选"),
    type: Optional[SeriesType] = Query(None, description="类型筛选"),
    search: Optional[str] = Query(None, description="搜索标题"),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    管理员获取专辑列表

    - 可查看所有状态的专辑
    - 支持搜索和筛选
    """
    query = select(Series)

    if status:
        query = query.filter(Series.status == status)
    if type:
        query = query.filter(Series.type == type)
    if search:
        query = query.filter(Series.title.ilike(f"%{search}%"))

    # 计数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 排序和分页
    query = (
        query.order_by(Series.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    series_list = result.scalars().all()

    return PaginatedSeriesResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if page_size > 0 and total > 0 else 0,
        items=[SeriesListResponse.model_validate(s) for s in series_list],
    )


@router.post(
    "",
    response_model=SeriesDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建专辑",
)
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def admin_create_series(
    request: Request,
    data: SeriesCreate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    创建新专辑

    - 初始状态可以是草稿或已发布
    """
    series = Series(
        title=data.title,
        description=data.description,
        cover_image=data.cover_image,
        type=data.type,
        status=data.status,
        display_order=data.display_order,
        is_featured=data.is_featured,
        created_by=current_admin.id,
    )

    db.add(series)
    await db.commit()
    await db.refresh(series)

    # 清除缓存
    await Cache.delete_pattern("series_*")
    await Cache.delete_pattern("featured_series:*")

    return SeriesDetailResponse(
        id=series.id,
        title=series.title,
        description=series.description,
        cover_image=series.cover_image,
        type=series.type,
        status=series.status,
        total_episodes=0,
        total_views=0,
        total_favorites=0,
        display_order=series.display_order,
        is_featured=series.is_featured,
        created_at=series.created_at,
        updated_at=series.updated_at,
        videos=[],
    )


@router.get(
    "/{series_id}",
    response_model=SeriesDetailResponse,
    summary="获取专辑详情（管理员）",
)
@limiter.limit(RateLimitPresets.ADMIN_READ)
async def admin_get_series_detail(
    request: Request,
    series_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    管理员获取专辑详情

    - 可查看任何状态的专辑
    - 包含完整的视频列表
    """
    result = await db.execute(
        select(Series)
        .filter(Series.id == series_id)
        .options(selectinload(Series.videos))
    )
    series = result.scalar_one_or_none()

    if not series:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="专辑不存在")

    # 查询视频详情和顺序
    series_videos_query = await db.execute(
        select(
            Video.id,
            Video.title,
            Video.poster_url,
            Video.duration,
            Video.view_count,
            series_videos.c.episode_number,
            series_videos.c.added_at,
        )
        .join(series_videos, Video.id == series_videos.c.video_id)
        .filter(series_videos.c.series_id == series_id)
        .order_by(series_videos.c.episode_number.asc())
    )
    video_rows = series_videos_query.all()

    videos = [
        SeriesVideoItem(
            video_id=row.id,
            episode_number=row.episode_number,
            title=row.title,
            poster_url=row.poster_url,
            duration=row.duration,
            view_count=row.view_count,
            added_at=row.added_at,
        )
        for row in video_rows
    ]

    return SeriesDetailResponse(
        id=series.id,
        title=series.title,
        description=series.description,
        cover_image=series.cover_image,
        type=series.type,
        status=series.status,
        total_episodes=series.total_episodes,
        total_views=series.total_views,
        total_favorites=series.total_favorites,
        display_order=series.display_order,
        is_featured=series.is_featured,
        created_at=series.created_at,
        updated_at=series.updated_at,
        videos=videos,
    )


@router.put("/{series_id}", response_model=SeriesDetailResponse, summary="更新专辑")
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def admin_update_series(
    request: Request,
    series_id: int,
    data: SeriesUpdate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新专辑信息
    """
    result = await db.execute(select(Series).filter(Series.id == series_id))
    series = result.scalar_one_or_none()

    if not series:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="专辑不存在")

    # 更新字段
    if data.title is not None:
        series.title = data.title
    if data.description is not None:
        series.description = data.description
    if data.cover_image is not None:
        series.cover_image = data.cover_image
    if data.type is not None:
        series.type = data.type
    if data.status is not None:
        series.status = data.status
    if data.display_order is not None:
        series.display_order = data.display_order
    if data.is_featured is not None:
        series.is_featured = data.is_featured

    await db.commit()
    await db.refresh(series)

    # 清除缓存
    await Cache.delete_pattern(f"series_detail:{series_id}")
    await Cache.delete_pattern("series_list:*")
    await Cache.delete_pattern("featured_series:*")

    # 返回更新后的详情
    return await admin_get_series_detail(request, series_id, current_admin, db)


@router.delete(
    "/{series_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除专辑"
)
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def admin_delete_series(
    request: Request,
    series_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除专辑

    - 会自动移除专辑与视频的关联
    - 不会删除视频本身
    """
    result = await db.execute(select(Series).filter(Series.id == series_id))
    series = result.scalar_one_or_none()

    if not series:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="专辑不存在")

    await db.delete(series)
    await db.commit()

    # 清除缓存
    await Cache.delete_pattern(f"series_detail:{series_id}")
    await Cache.delete_pattern("series_list:*")
    await Cache.delete_pattern("featured_series:*")

    return None


@router.post("/{series_id}/videos", summary="添加视频到专辑")
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def admin_add_videos_to_series(
    request: Request,
    series_id: int,
    data: SeriesAddVideos,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    添加视频到专辑

    - 可以指定起始集数（自动递增）
    - 如果不指定，自动从现有最大集数+1开始
    """
    # 检查专辑是否存在
    result = await db.execute(select(Series).filter(Series.id == series_id))
    series = result.scalar_one_or_none()

    if not series:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="专辑不存在")

    # 检查视频是否存在
    videos_result = await db.execute(
        select(Video.id).filter(Video.id.in_(data.video_ids))
    )
    existing_video_ids = {row[0] for row in videos_result.all()}
    missing_ids = set(data.video_ids) - existing_video_ids

    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"视频不存在: {list(missing_ids)}",
        )

    # 获取当前最大集数
    if data.start_episode_number is None:
        max_episode_result = await db.execute(
            select(func.max(series_videos.c.episode_number)).where(
                series_videos.c.series_id == series_id
            )
        )
        max_episode = max_episode_result.scalar() or 0
        start_num = max_episode + 1
    else:
        start_num = data.start_episode_number

    # 添加视频
    values = [
        {
            "series_id": series_id,
            "video_id": video_id,
            "episode_number": start_num + idx,
        }
        for idx, video_id in enumerate(data.video_ids)
    ]

    await db.execute(series_videos.insert().values(values))

    # 更新专辑统计
    series.total_episodes += len(data.video_ids)
    await db.commit()

    # 清除缓存
    await Cache.delete_pattern(f"series_detail:{series_id}")

    return {
        "message": f"成功添加 {len(data.video_ids)} 个视频",
        "added_count": len(data.video_ids),
    }


@router.delete("/{series_id}/videos", summary="从专辑移除视频")
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def admin_remove_videos_from_series(
    request: Request,
    series_id: int,
    data: SeriesRemoveVideos,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    从专辑移除视频
    """
    # 检查专辑是否存在
    result = await db.execute(select(Series).filter(Series.id == series_id))
    series = result.scalar_one_or_none()

    if not series:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="专辑不存在")

    # 移除视频
    delete_stmt = delete(series_videos).where(
        and_(
            series_videos.c.series_id == series_id,
            series_videos.c.video_id.in_(data.video_ids),
        )
    )
    result = await db.execute(delete_stmt)
    removed_count = result.rowcount

    # 更新专辑统计
    series.total_episodes -= removed_count
    if series.total_episodes < 0:
        series.total_episodes = 0

    await db.commit()

    # 清除缓存
    await Cache.delete_pattern(f"series_detail:{series_id}")

    return {
        "message": f"成功移除 {removed_count} 个视频",
        "removed_count": removed_count,
    }


@router.put("/{series_id}/videos/order", summary="更新视频顺序")
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def admin_update_video_order(
    request: Request,
    series_id: int,
    data: SeriesUpdateVideoOrder,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新专辑中视频的顺序

    - 传入新的视频顺序列表
    - 格式: [{"video_id": 1, "episode_number": 1}, ...]
    """
    # 检查专辑是否存在
    result = await db.execute(select(Series).filter(Series.id == series_id))
    series = result.scalar_one_or_none()

    if not series:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="专辑不存在")

    # 更新每个视频的集数
    for item in data.video_order:
        video_id = item.get("video_id")
        episode_number = item.get("episode_number")

        if video_id is None or episode_number is None:
            continue

        # 更新集数
        update_stmt = (
            series_videos.update()
            .where(
                and_(
                    series_videos.c.series_id == series_id,
                    series_videos.c.video_id == video_id,
                )
            )
            .values(episode_number=episode_number)
        )
        await db.execute(update_stmt)

    await db.commit()

    # 清除缓存
    await Cache.delete_pattern(f"series_detail:{series_id}")

    return {
        "message": "视频顺序更新成功",
        "updated_count": len(data.video_order),
    }
