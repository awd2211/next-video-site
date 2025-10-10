"""
视频专辑/系列 - 公共API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional
import math

from app.database import get_db
from app.models.series import Series, SeriesType, SeriesStatus, series_videos
from app.models.video import Video
from app.schemas.series import (
    SeriesListResponse,
    SeriesDetailResponse,
    PaginatedSeriesResponse,
    SeriesVideoItem,
)
from app.utils.cache import Cache
from app.utils.rate_limit import limiter, RateLimitPresets
import hashlib

router = APIRouter()


@router.get("", response_model=PaginatedSeriesResponse, summary="获取专辑列表")
@limiter.limit(RateLimitPresets.RELAXED)
async def get_series_list(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[SeriesType] = Query(None, description="专辑类型筛选"),
    is_featured: Optional[bool] = Query(None, description="是否只看推荐"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取专辑列表 (已发布)

    - 支持分页
    - 支持按类型筛选
    - 支持只看推荐
    - 缓存5分钟
    """
    # 生成缓存键
    cache_key = hashlib.md5(
        f"series_list:{page}:{page_size}:{type}:{is_featured}".encode()
    ).hexdigest()
    cached = await Cache.get(cache_key)
    if cached:
        return cached

    # 构建查询
    query = select(Series).filter(Series.status == SeriesStatus.PUBLISHED)

    if type:
        query = query.filter(Series.type == type)
    if is_featured is not None:
        query = query.filter(Series.is_featured == is_featured)

    # 计数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 排序和分页
    query = (
        query.order_by(Series.display_order.desc(), Series.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    series_list = result.scalars().all()

    # Build response items with video_count alias
    items = []
    for s in series_list:
        item_dict = SeriesListResponse.model_validate(s).model_dump()
        item_dict['video_count'] = item_dict['total_episodes']  # Add alias
        items.append(SeriesListResponse(**item_dict))

    response = PaginatedSeriesResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if page_size > 0 else 0,
        items=items,
    )

    # 缓存5分钟
    await Cache.set(cache_key, response, ttl=300)
    return response


@router.get("/{series_id}", response_model=SeriesDetailResponse, summary="获取专辑详情")
@limiter.limit(RateLimitPresets.RELAXED)
async def get_series_detail(
    request: Request,
    series_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    获取专辑详情 (含视频列表)

    - 只能查看已发布的专辑
    - 视频按集数排序
    - 缓存5分钟
    """
    cache_key = f"series_detail:{series_id}"
    cached = await Cache.get(cache_key)
    if cached:
        return cached

    # 查询专辑
    result = await db.execute(
        select(Series)
        .filter(
            Series.id == series_id,
            Series.status == SeriesStatus.PUBLISHED
        )
        .options(selectinload(Series.videos))
    )
    series = result.scalar_one_or_none()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="专辑不存在或未发布"
        )

    # 查询视频详情
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

    # 构建视频列表
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

    response = SeriesDetailResponse(
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

    # 缓存5分钟
    await Cache.set(cache_key, response, ttl=300)
    return response


@router.get("/featured/list", response_model=list[SeriesListResponse], summary="获取推荐专辑")
@limiter.limit(RateLimitPresets.RELAXED)
async def get_featured_series(
    request: Request,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    获取推荐专辑列表

    - 只返回已发布且推荐的专辑
    - 按显示顺序排序
    - 缓存10分钟
    """
    cache_key = f"featured_series:{limit}"
    cached = await Cache.get(cache_key)
    if cached:
        return cached

    result = await db.execute(
        select(Series)
        .filter(
            Series.status == SeriesStatus.PUBLISHED,
            Series.is_featured == True
        )
        .order_by(Series.display_order.desc(), Series.created_at.desc())
        .limit(limit)
    )
    series_list = result.scalars().all()

    # Build response with video_count alias
    response = []
    for s in series_list:
        item_dict = SeriesListResponse.model_validate(s).model_dump()
        item_dict['video_count'] = item_dict['total_episodes']  # Add alias
        response.append(SeriesListResponse(**item_dict))

    # 缓存10分钟
    await Cache.set(cache_key, response, ttl=600)
    return response
