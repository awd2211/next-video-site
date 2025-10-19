"""
Season (季度) 管理 - Admin API

提供电视剧季度的完整CRUD管理接口
"""

import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.episode import Episode
from app.models.season import Season, SeasonStatus
from app.models.series import Series
from app.models.user import AdminUser
from app.schemas.season import (
    BatchArchiveSeasons,
    BatchDeleteSeasons,
    BatchPublishSeasons,
    PaginatedSeasonResponse,
    SeasonCreate,
    SeasonDetailResponse,
    SeasonListResponse,
    SeasonUpdate,
    EpisodeInSeasonResponse,
)
from app.utils.cache import Cache
from app.utils.dependencies import get_current_admin_user
from app.utils.rate_limit import RateLimitPresets, limiter
from app.utils.sorting import apply_sorting, normalize_sort_field

router = APIRouter()


@router.get(
    "/series/{series_id}/seasons",
    response_model=PaginatedSeasonResponse,
    summary="获取剧集的所有季度",
)
@limiter.limit(RateLimitPresets.ADMIN_READ)
async def list_seasons_by_series(
    request: Request,
    series_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[SeasonStatus] = Query(None, description="状态筛选"),
    search: Optional[str] = Query(None, description="搜索标题"),
    sort_by: Optional[str] = Query(
        "season_number",
        description="排序字段: id, season_number, title, status, total_episodes, view_count, created_at",
    ),
    sort_order: Optional[str] = Query(
        "asc", regex="^(asc|desc)$", description="排序顺序: asc 或 desc"
    ),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取指定剧集的所有季度列表

    - 可按状态筛选
    - 支持标题搜索
    - 支持排序
    """
    # 先验证 Series 是否存在
    series_result = await db.execute(select(Series).filter(Series.id == series_id))
    series = series_result.scalar_one_or_none()
    if not series:
        raise HTTPException(status_code=404, detail="剧集不存在")

    # 构建查询
    query = select(Season).filter(Season.series_id == series_id)

    # 筛选条件
    if status:
        query = query.filter(Season.status == status)
    if search:
        query = query.filter(Season.title.ilike(f"%{search}%"))

    # 计数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 排序
    sort_field = normalize_sort_field(sort_by)
    allowed_sort_fields = [
        "id",
        "season_number",
        "title",
        "status",
        "total_episodes",
        "view_count",
        "created_at",
    ]
    query = apply_sorting(
        query,
        Season,
        sort_field,
        sort_order,
        default_sort="season_number",
        allowed_fields=allowed_sort_fields,
    )

    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    seasons = result.scalars().all()

    return PaginatedSeasonResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if page_size > 0 and total > 0 else 0,
        items=[SeasonListResponse.model_validate(s) for s in seasons],
    )


@router.post(
    "/series/{series_id}/seasons",
    response_model=SeasonDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建新季度",
)
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def create_season(
    request: Request,
    series_id: int,
    data: SeasonCreate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    为指定剧集创建新季度

    - 自动验证 series_id 和 season_number 的唯一性
    - 初始 total_episodes = 0（添加剧集时自动更新）
    """
    # 验证 Series 是否存在
    series_result = await db.execute(select(Series).filter(Series.id == series_id))
    series = series_result.scalar_one_or_none()
    if not series:
        raise HTTPException(status_code=404, detail="剧集不存在")

    # 检查 season_number 是否已存在
    existing = await db.execute(
        select(Season).filter(
            Season.series_id == series_id,
            Season.season_number == data.season_number,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"第{data.season_number}季已存在",
        )

    # 创建 Season
    season = Season(
        series_id=series_id,
        season_number=data.season_number,
        title=data.title,
        description=data.description,
        status=data.status,
        vip_required=data.vip_required,
        poster_url=data.poster_url,
        backdrop_url=data.backdrop_url,
        trailer_url=data.trailer_url,
        release_date=data.release_date,
        is_featured=data.is_featured,
        sort_order=data.sort_order,
        total_episodes=0,
        total_duration=0,
        view_count=0,
        favorite_count=0,
        average_rating=0.0,
    )

    db.add(season)
    await db.commit()
    await db.refresh(season)

    # 清除缓存
    await Cache.delete_pattern(f"series_detail:{series_id}")
    await Cache.delete_pattern("series_list:*")

    return SeasonDetailResponse(
        **season.__dict__,
        episodes=[],
    )


@router.get(
    "/seasons/{season_id}",
    response_model=SeasonDetailResponse,
    summary="获取季度详情",
)
@limiter.limit(RateLimitPresets.ADMIN_READ)
async def get_season_detail(
    request: Request,
    season_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取季度详细信息

    - 包含该季下的所有剧集列表
    - 剧集按 episode_number 排序
    """
    result = await db.execute(
        select(Season)
        .filter(Season.id == season_id)
        .options(selectinload(Season.episodes))
    )
    season = result.scalar_one_or_none()

    if not season:
        raise HTTPException(status_code=404, detail="季度不存在")

    # 转换 episodes 为响应格式
    episodes_response = [
        EpisodeInSeasonResponse.model_validate(ep) for ep in season.episodes
    ]

    return SeasonDetailResponse(
        **season.__dict__,
        episodes=episodes_response,
    )


@router.put(
    "/seasons/{season_id}",
    response_model=SeasonDetailResponse,
    summary="更新季度信息",
)
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def update_season(
    request: Request,
    season_id: int,
    data: SeasonUpdate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新季度信息

    - 只更新提供的字段
    - 自动处理发布状态变更（设置 published_at）
    """
    result = await db.execute(select(Season).filter(Season.id == season_id))
    season = result.scalar_one_or_none()

    if not season:
        raise HTTPException(status_code=404, detail="季度不存在")

    # 更新字段
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(season, key, value)

    # 如果状态改为已发布且之前未发布，设置 published_at
    if (
        data.status == SeasonStatus.PUBLISHED
        and season.status != SeasonStatus.PUBLISHED
        and season.published_at is None
    ):
        from datetime import datetime, timezone
        season.published_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(season, ["episodes"])

    # 清除缓存
    await Cache.delete_pattern(f"season_detail:{season_id}")
    await Cache.delete_pattern(f"series_detail:{season.series_id}")

    episodes_response = [
        EpisodeInSeasonResponse.model_validate(ep) for ep in season.episodes
    ]

    return SeasonDetailResponse(
        **season.__dict__,
        episodes=episodes_response,
    )


@router.delete(
    "/seasons/{season_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除季度",
)
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def delete_season(
    request: Request,
    season_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除季度

    - 会级联删除该季下的所有剧集（Episodes）
    - 不会删除关联的视频文件（Videos）
    """
    result = await db.execute(select(Season).filter(Season.id == season_id))
    season = result.scalar_one_or_none()

    if not season:
        raise HTTPException(status_code=404, detail="季度不存在")

    series_id = season.series_id

    await db.delete(season)
    await db.commit()

    # 清除缓存
    await Cache.delete_pattern(f"season_detail:{season_id}")
    await Cache.delete_pattern(f"series_detail:{series_id}")

    return None


# ==================== 批量操作 ====================


@router.post(
    "/seasons/batch/publish",
    summary="批量发布季度",
)
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def batch_publish_seasons(
    request: Request,
    data: BatchPublishSeasons,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """批量将季度状态改为已发布"""
    result = await db.execute(
        select(Season).filter(Season.id.in_(data.season_ids))
    )
    seasons = result.scalars().all()

    if not seasons:
        raise HTTPException(status_code=404, detail="未找到任何季度")

    count = 0
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)

    for season in seasons:
        if season.status != SeasonStatus.PUBLISHED:
            season.status = SeasonStatus.PUBLISHED
            if season.published_at is None:
                season.published_at = now
            count += 1

    await db.commit()

    # 清除缓存
    await Cache.delete_pattern("season_*")
    await Cache.delete_pattern("series_*")

    return {
        "message": f"成功发布 {count} 个季度",
        "updated_count": count,
    }


@router.post(
    "/seasons/batch/archive",
    summary="批量归档季度",
)
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def batch_archive_seasons(
    request: Request,
    data: BatchArchiveSeasons,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """批量将季度状态改为已归档"""
    result = await db.execute(
        select(Season).filter(Season.id.in_(data.season_ids))
    )
    seasons = result.scalars().all()

    if not seasons:
        raise HTTPException(status_code=404, detail="未找到任何季度")

    count = 0
    for season in seasons:
        if season.status != SeasonStatus.ARCHIVED:
            season.status = SeasonStatus.ARCHIVED
            count += 1

    await db.commit()

    # 清除缓存
    await Cache.delete_pattern("season_*")
    await Cache.delete_pattern("series_*")

    return {
        "message": f"成功归档 {count} 个季度",
        "updated_count": count,
    }


@router.post(
    "/seasons/batch/delete",
    summary="批量删除季度",
)
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def batch_delete_seasons(
    request: Request,
    data: BatchDeleteSeasons,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    批量删除季度

    - 需要确认操作（confirm=true）
    - 会级联删除所有关联的剧集
    """
    result = await db.execute(
        select(Season).filter(Season.id.in_(data.season_ids))
    )
    seasons = result.scalars().all()

    if not seasons:
        raise HTTPException(status_code=404, detail="未找到任何季度")

    count = len(seasons)

    for season in seasons:
        await db.delete(season)

    await db.commit()

    # 清除缓存
    await Cache.delete_pattern("season_*")
    await Cache.delete_pattern("series_*")

    return {
        "message": f"成功删除 {count} 个季度",
        "deleted_count": count,
    }


# ==================== 统计与分析 ====================


@router.get(
    "/seasons/{season_id}/stats",
    summary="获取季度统计数据",
)
@limiter.limit(RateLimitPresets.ADMIN_READ)
async def get_season_stats(
    request: Request,
    season_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取季度的统计数据

    返回：
    - 总集数
    - 总观看量
    - 平均完播率
    - 每集观看量分布
    """
    result = await db.execute(
        select(Season)
        .filter(Season.id == season_id)
        .options(selectinload(Season.episodes))
    )
    season = result.scalar_one_or_none()

    if not season:
        raise HTTPException(status_code=404, detail="季度不存在")

    # 计算每集的观看量
    episode_views = [
        {"episode_number": ep.episode_number, "view_count": ep.view_count}
        for ep in season.episodes
    ]

    return {
        "season_id": season_id,
        "season_number": season.season_number,
        "total_episodes": season.total_episodes,
        "total_views": season.view_count,
        "total_favorites": season.favorite_count,
        "average_rating": season.average_rating,
        "episode_views": episode_views,
    }
