"""
Episode (单集) 管理 - Admin API

提供电视剧单集的完整CRUD管理接口，包括批量操作和片头片尾设置
"""

import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.episode import Episode, EpisodeStatus
from app.models.season import Season
from app.models.user import AdminUser
from app.models.video import Video
from app.schemas.episode import (
    BatchAddEpisodes,
    BatchDeleteEpisodes,
    BatchPublishEpisodes,
    BatchSetIntroMarkers,
    BatchUpdateEpisodesOrder,
    EpisodeCreate,
    EpisodeDetailResponse,
    EpisodeListResponse,
    EpisodeUpdate,
    PaginatedEpisodeResponse,
    VideoInEpisodeResponse,
)
from app.utils.cache import Cache
from app.utils.dependencies import get_current_admin_user
from app.utils.rate_limit import RateLimitPresets, limiter
from app.utils.sorting import apply_sorting, normalize_sort_field

router = APIRouter()


@router.get(
    "/seasons/{season_id}/episodes",
    response_model=PaginatedEpisodeResponse,
    summary="获取季度下的所有剧集",
)
@limiter.limit(RateLimitPresets.ADMIN_READ)
async def list_episodes_by_season(
    request: Request,
    season_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    status: Optional[EpisodeStatus] = Query(None, description="状态筛选"),
    search: Optional[str] = Query(None, description="搜索标题"),
    sort_by: Optional[str] = Query(
        "episode_number",
        description="排序字段: id, episode_number, title, status, view_count, created_at",
    ),
    sort_order: Optional[str] = Query(
        "asc", regex="^(asc|desc)$", description="排序顺序: asc 或 desc"
    ),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取指定季度的所有剧集列表

    - 可按状态筛选
    - 支持标题搜索
    - 默认按集数排序
    """
    # 验证 Season 是否存在
    season_result = await db.execute(select(Season).filter(Season.id == season_id))
    season = season_result.scalar_one_or_none()
    if not season:
        raise HTTPException(status_code=404, detail="季度不存在")

    # 构建查询
    query = select(Episode).filter(Episode.season_id == season_id)

    # 筛选条件
    if status:
        query = query.filter(Episode.status == status)
    if search:
        query = query.filter(Episode.title.ilike(f"%{search}%"))

    # 计数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 排序
    sort_field = normalize_sort_field(sort_by)
    allowed_sort_fields = [
        "id",
        "episode_number",
        "title",
        "status",
        "view_count",
        "created_at",
    ]
    query = apply_sorting(
        query,
        Episode,
        sort_field,
        sort_order,
        default_sort="episode_number",
        allowed_fields=allowed_sort_fields,
    )

    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    episodes = result.scalars().all()

    return PaginatedEpisodeResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if page_size > 0 and total > 0 else 0,
        items=[EpisodeListResponse.model_validate(ep) for ep in episodes],
    )


@router.post(
    "/seasons/{season_id}/episodes",
    response_model=EpisodeDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建单集",
)
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def create_episode(
    request: Request,
    season_id: int,
    data: EpisodeCreate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    为指定季度创建新剧集

    - 自动验证 video_id 是否已被使用
    - 自动验证 episode_number 在该季内的唯一性
    - 自动更新 Season 的 total_episodes
    """
    # 验证 Season 是否存在
    season_result = await db.execute(select(Season).filter(Season.id == season_id))
    season = season_result.scalar_one_or_none()
    if not season:
        raise HTTPException(status_code=404, detail="季度不存在")

    # 验证 Video 是否存在且未被使用
    video_result = await db.execute(select(Video).filter(Video.id == data.video_id))
    video = video_result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    # 检查 Video 是否已关联到其他 Episode
    existing_episode = await db.execute(
        select(Episode).filter(Episode.video_id == data.video_id)
    )
    if existing_episode.scalar_one_or_none():
        raise HTTPException(
            status_code=400, detail="该视频已关联到其他剧集"
        )

    # 检查 episode_number 是否已存在
    existing_number = await db.execute(
        select(Episode).filter(
            Episode.season_id == season_id,
            Episode.episode_number == data.episode_number,
        )
    )
    if existing_number.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"第{data.episode_number}集已存在",
        )

    # 创建 Episode
    episode = Episode(
        season_id=season_id,
        video_id=data.video_id,
        episode_number=data.episode_number,
        title=data.title,
        description=data.description,
        intro_start=data.intro_start,
        intro_end=data.intro_end,
        credits_start=data.credits_start,
        next_episode_preview_url=data.next_episode_preview_url,
        preview_duration=data.preview_duration,
        is_free=data.is_free,
        vip_required=data.vip_required,
        status=data.status,
        release_date=data.release_date,
        is_featured=data.is_featured,
        sort_order=data.sort_order,
        view_count=0,
        like_count=0,
        comment_count=0,
    )

    db.add(episode)

    # 更新 Season 的 total_episodes
    season.total_episodes += 1

    await db.commit()
    await db.refresh(episode, ["video"])

    # 清除缓存
    await Cache.delete_pattern(f"season_detail:{season_id}")

    # 构建响应
    video_response = VideoInEpisodeResponse.model_validate(episode.video) if episode.video else None

    return EpisodeDetailResponse(
        **episode.__dict__,
        video=video_response,
    )


@router.get(
    "/episodes/{episode_id}",
    response_model=EpisodeDetailResponse,
    summary="获取剧集详情",
)
@limiter.limit(RateLimitPresets.ADMIN_READ)
async def get_episode_detail(
    request: Request,
    episode_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取剧集详细信息

    - 包含关联的视频详情
    """
    result = await db.execute(
        select(Episode)
        .filter(Episode.id == episode_id)
        .options(selectinload(Episode.video))
    )
    episode = result.scalar_one_or_none()

    if not episode:
        raise HTTPException(status_code=404, detail="剧集不存在")

    video_response = VideoInEpisodeResponse.model_validate(episode.video) if episode.video else None

    return EpisodeDetailResponse(
        **episode.__dict__,
        video=video_response,
    )


@router.put(
    "/episodes/{episode_id}",
    response_model=EpisodeDetailResponse,
    summary="更新剧集信息",
)
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def update_episode(
    request: Request,
    episode_id: int,
    data: EpisodeUpdate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新剧集信息

    - 只更新提供的字段
    - 支持更新片头片尾时间标记
    - 自动处理发布状态变更
    """
    result = await db.execute(
        select(Episode)
        .filter(Episode.id == episode_id)
        .options(selectinload(Episode.video))
    )
    episode = result.scalar_one_or_none()

    if not episode:
        raise HTTPException(status_code=404, detail="剧集不存在")

    # 更新字段
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(episode, key, value)

    # 如果状态改为已发布且之前未发布，设置 published_at
    if (
        data.status == EpisodeStatus.PUBLISHED
        and episode.status != EpisodeStatus.PUBLISHED
        and episode.published_at is None
    ):
        from datetime import datetime, timezone
        episode.published_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(episode)

    # 清除缓存
    await Cache.delete_pattern(f"episode_detail:{episode_id}")
    await Cache.delete_pattern(f"season_detail:{episode.season_id}")

    video_response = VideoInEpisodeResponse.model_validate(episode.video) if episode.video else None

    return EpisodeDetailResponse(
        **episode.__dict__,
        video=video_response,
    )


@router.delete(
    "/episodes/{episode_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除剧集",
)
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def delete_episode(
    request: Request,
    episode_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除剧集

    - 不会删除关联的视频文件
    - 自动更新 Season 的 total_episodes
    """
    result = await db.execute(select(Episode).filter(Episode.id == episode_id))
    episode = result.scalar_one_or_none()

    if not episode:
        raise HTTPException(status_code=404, detail="剧集不存在")

    season_id = episode.season_id

    # 更新 Season 的 total_episodes
    season = await db.get(Season, season_id)
    if season:
        season.total_episodes = max(0, season.total_episodes - 1)

    await db.delete(episode)
    await db.commit()

    # 清除缓存
    await Cache.delete_pattern(f"episode_detail:{episode_id}")
    await Cache.delete_pattern(f"season_detail:{season_id}")

    return None


# ==================== 批量操作 ====================


@router.post(
    "/seasons/{season_id}/episodes/batch",
    summary="批量添加剧集",
)
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def batch_add_episodes(
    request: Request,
    season_id: int,
    data: BatchAddEpisodes,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    批量添加剧集

    - 一次性添加多个视频作为连续的集
    - 自动生成集数和标题
    - 自动更新 Season 的 total_episodes

    示例：
    - video_ids: [101, 102, 103]
    - start_episode_number: 1
    - 结果：第1集、第2集、第3集
    """
    # 验证 Season 是否存在
    season_result = await db.execute(select(Season).filter(Season.id == season_id))
    season = season_result.scalar_one_or_none()
    if not season:
        raise HTTPException(status_code=404, detail="季度不存在")

    # 验证所有 Video 是否存在
    videos_result = await db.execute(
        select(Video).filter(Video.id.in_(data.video_ids))
    )
    existing_videos = {v.id: v for v in videos_result.scalars().all()}

    missing_ids = set(data.video_ids) - set(existing_videos.keys())
    if missing_ids:
        raise HTTPException(
            status_code=404,
            detail=f"视频不存在: {list(missing_ids)}",
        )

    # 检查是否有视频已被使用
    used_videos_result = await db.execute(
        select(Episode.video_id).filter(Episode.video_id.in_(data.video_ids))
    )
    used_video_ids = {row[0] for row in used_videos_result.all()}
    if used_video_ids:
        raise HTTPException(
            status_code=400,
            detail=f"以下视频已关联到其他剧集: {list(used_video_ids)}",
        )

    # 创建剧集
    episodes_created = []
    current_episode_number = data.start_episode_number

    for idx, video_id in enumerate(data.video_ids):
        # 生成标题
        if data.auto_title:
            title = f"{data.title_prefix}{current_episode_number}{data.title_suffix}"
        else:
            video = existing_videos[video_id]
            title = video.title

        episode = Episode(
            season_id=season_id,
            video_id=video_id,
            episode_number=current_episode_number,
            title=title,
            is_free=data.is_free,
            vip_required=data.vip_required,
            status=data.status,
            view_count=0,
            like_count=0,
            comment_count=0,
        )

        db.add(episode)
        episodes_created.append(episode)
        current_episode_number += 1

    # 更新 Season 的 total_episodes
    season.total_episodes += len(episodes_created)

    await db.commit()

    # 清除缓存
    await Cache.delete_pattern(f"season_detail:{season_id}")

    return {
        "message": f"成功添加 {len(episodes_created)} 集",
        "count": len(episodes_created),
        "episodes": [
            {
                "id": ep.id,
                "episode_number": ep.episode_number,
                "title": ep.title,
            }
            for ep in episodes_created
        ],
    }


@router.put(
    "/seasons/{season_id}/episodes/order",
    summary="更新剧集顺序",
)
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def batch_update_episodes_order(
    request: Request,
    season_id: int,
    data: BatchUpdateEpisodesOrder,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    批量更新剧集顺序

    用于拖拽排序后保存新顺序

    示例输入：
    {
      "episode_orders": [
        {"episode_id": 1, "episode_number": 2},
        {"episode_id": 2, "episode_number": 1}
      ]
    }
    """
    # 验证 Season 是否存在
    season_result = await db.execute(select(Season).filter(Season.id == season_id))
    season = season_result.scalar_one_or_none()
    if not season:
        raise HTTPException(status_code=404, detail="季度不存在")

    # 更新每个剧集的集数
    updated_count = 0
    for item in data.episode_orders:
        episode_id = item.get("episode_id")
        new_episode_number = item.get("episode_number")

        if episode_id is None or new_episode_number is None:
            continue

        result = await db.execute(
            select(Episode).filter(
                Episode.id == episode_id, Episode.season_id == season_id
            )
        )
        episode = result.scalar_one_or_none()

        if episode:
            episode.episode_number = new_episode_number
            updated_count += 1

    await db.commit()

    # 清除缓存
    await Cache.delete_pattern(f"season_detail:{season_id}")

    return {
        "message": f"成功更新 {updated_count} 集的顺序",
        "updated_count": updated_count,
    }


@router.post(
    "/episodes/batch/intro-markers",
    summary="批量设置片头片尾时间标记",
)
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def batch_set_intro_markers(
    request: Request,
    data: BatchSetIntroMarkers,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    批量设置片头片尾时间标记

    适用于整季都有相同片头片尾时长的情况

    示例：
    - intro_start: 0
    - intro_end: 90 (片头90秒)
    - credits_start: 2700 (片尾从45分钟开始)
    """
    result = await db.execute(
        select(Episode).filter(Episode.id.in_(data.episode_ids))
    )
    episodes = result.scalars().all()

    if not episodes:
        raise HTTPException(status_code=404, detail="未找到任何剧集")

    count = 0
    for episode in episodes:
        if data.intro_start is not None:
            episode.intro_start = data.intro_start
        if data.intro_end is not None:
            episode.intro_end = data.intro_end
        if data.credits_start is not None:
            episode.credits_start = data.credits_start
        count += 1

    await db.commit()

    # 清除缓存
    season_ids = {ep.season_id for ep in episodes}
    for season_id in season_ids:
        await Cache.delete_pattern(f"season_detail:{season_id}")

    return {
        "message": f"成功设置 {count} 集的片头片尾标记",
        "updated_count": count,
    }


@router.post(
    "/episodes/batch/publish",
    summary="批量发布剧集",
)
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def batch_publish_episodes(
    request: Request,
    data: BatchPublishEpisodes,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """批量将剧集状态改为已发布"""
    result = await db.execute(
        select(Episode).filter(Episode.id.in_(data.episode_ids))
    )
    episodes = result.scalars().all()

    if not episodes:
        raise HTTPException(status_code=404, detail="未找到任何剧集")

    count = 0
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)

    for episode in episodes:
        if episode.status != EpisodeStatus.PUBLISHED:
            episode.status = EpisodeStatus.PUBLISHED
            if episode.published_at is None:
                episode.published_at = now
            count += 1

    await db.commit()

    # 清除缓存
    season_ids = {ep.season_id for ep in episodes}
    for season_id in season_ids:
        await Cache.delete_pattern(f"season_detail:{season_id}")

    return {
        "message": f"成功发布 {count} 集",
        "updated_count": count,
    }


@router.post(
    "/episodes/batch/delete",
    summary="批量删除剧集",
)
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def batch_delete_episodes(
    request: Request,
    data: BatchDeleteEpisodes,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    批量删除剧集

    - 需要确认操作（confirm=true）
    - 不会删除关联的视频文件
    - 自动更新 Season 的 total_episodes
    """
    result = await db.execute(
        select(Episode).filter(Episode.id.in_(data.episode_ids))
    )
    episodes = result.scalars().all()

    if not episodes:
        raise HTTPException(status_code=404, detail="未找到任何剧集")

    # 按 season 分组统计
    season_counts: dict[int, int] = {}
    for episode in episodes:
        season_counts[episode.season_id] = season_counts.get(episode.season_id, 0) + 1

    count = len(episodes)

    # 删除剧集
    for episode in episodes:
        await db.delete(episode)

    # 更新 Season 的 total_episodes
    for season_id, deleted_count in season_counts.items():
        season = await db.get(Season, season_id)
        if season:
            season.total_episodes = max(0, season.total_episodes - deleted_count)

    await db.commit()

    # 清除缓存
    for season_id in season_counts.keys():
        await Cache.delete_pattern(f"season_detail:{season_id}")

    return {
        "message": f"成功删除 {count} 集",
        "deleted_count": count,
    }
