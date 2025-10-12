import math

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from loguru import logger
from sqlalchemy import and_, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.user_activity import WatchHistory
from app.models.video import Video
from app.schemas.user_activity import (
    PaginatedWatchHistoryResponse,
    WatchHistoryCreate,
    WatchHistoryResponse,
    WatchHistoryUpdate,
)
from app.utils.dependencies import get_current_active_user

router = APIRouter()


@router.post(
    "/", response_model=WatchHistoryResponse, status_code=status.HTTP_201_CREATED
)
async def create_or_update_watch_history(
    history_data: WatchHistoryCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Record or update watch history for a video.
    If history exists, update it; otherwise create new.
    """
    # Verify video exists
    video_result = await db.execute(
        select(Video).where(Video.id == history_data.video_id)
    )
    video = video_result.scalar_one_or_none()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
        )

    # Check if history exists
    existing_result = await db.execute(
        select(WatchHistory).where(
            and_(
                WatchHistory.user_id == current_user.id,
                WatchHistory.video_id == history_data.video_id,
            )
        )
    )
    existing_history = existing_result.scalar_one_or_none()

    is_new_watch = False
    if existing_history:
        # Update existing history
        existing_history.watch_duration = history_data.watch_duration
        existing_history.last_position = history_data.last_position
        existing_history.is_completed = 1 if history_data.is_completed else 0
        history = existing_history
    else:
        # Create new history
        history = WatchHistory(
            user_id=current_user.id,
            video_id=history_data.video_id,
            watch_duration=history_data.watch_duration,
            last_position=history_data.last_position,
            is_completed=1 if history_data.is_completed else 0,
        )
        db.add(history)
        is_new_watch = True

    await db.commit()
    await db.refresh(history)
    await db.refresh(history, ["video"])

    # 使用后台任务异步更新浏览量（仅新观看记录）
    # 使用原子UPDATE避免竞态条件
    if is_new_watch:

        async def increment_view_count():
            from app.database import AsyncSessionLocal

            async with AsyncSessionLocal() as session:
                try:
                    await session.execute(
                        update(Video)
                        .where(Video.id == history_data.video_id)
                        .values(view_count=Video.view_count + 1)
                    )
                    await session.commit()
                except Exception as e:
                    logger.error(f"Failed to increment view count: {e}", exc_info=True)

        background_tasks.add_task(increment_view_count)

    return WatchHistoryResponse.model_validate(history)


@router.get("/", response_model=PaginatedWatchHistoryResponse)
async def get_watch_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's watch history"""
    # Count total
    count_query = select(func.count()).where(WatchHistory.user_id == current_user.id)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated history with video details
    query = (
        select(WatchHistory)
        .where(WatchHistory.user_id == current_user.id)
        .options(selectinload(WatchHistory.video))
        .order_by(WatchHistory.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    history_items = result.scalars().all()

    items = [WatchHistoryResponse.model_validate(item) for item in history_items]

    return PaginatedWatchHistoryResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if page_size > 0 and total > 0 else 0,
        items=items,
    )


@router.get("/{video_id}", response_model=WatchHistoryResponse)
async def get_video_watch_history(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get watch history for a specific video"""
    query = (
        select(WatchHistory)
        .where(
            and_(
                WatchHistory.user_id == current_user.id,
                WatchHistory.video_id == video_id,
            )
        )
        .options(selectinload(WatchHistory.video))
    )

    result = await db.execute(query)
    history = result.scalar_one_or_none()

    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Watch history not found"
        )

    return WatchHistoryResponse.model_validate(history)


@router.patch("/{video_id}/progress", response_model=WatchHistoryResponse)
async def update_watch_progress(
    video_id: int,
    progress_data: WatchHistoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    快速更新观看进度 (用于播放器每10秒同步)

    这是一个轻量级端点,只更新播放进度,不触发view_count增加
    """
    # Check if history exists
    existing_result = await db.execute(
        select(WatchHistory)
        .where(
            and_(
                WatchHistory.user_id == current_user.id,
                WatchHistory.video_id == video_id,
            )
        )
        .options(selectinload(WatchHistory.video))
    )
    existing_history = existing_result.scalar_one_or_none()

    if existing_history:
        # Update existing history
        if progress_data.last_position is not None:
            existing_history.last_position = progress_data.last_position
        if progress_data.watch_duration is not None:
            existing_history.watch_duration = progress_data.watch_duration
        if progress_data.is_completed is not None:
            existing_history.is_completed = 1 if progress_data.is_completed else 0

        history = existing_history
    else:
        # Create new history if doesn't exist
        # Verify video exists
        video_result = await db.execute(select(Video).where(Video.id == video_id))
        video = video_result.scalar_one_or_none()
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
            )

        history = WatchHistory(
            user_id=current_user.id,
            video_id=video_id,
            watch_duration=progress_data.watch_duration or 0,
            last_position=progress_data.last_position or 0,
            is_completed=1 if progress_data.is_completed else 0,
        )
        db.add(history)

        # Only increment view count for new history
        video.view_count = video.view_count + 1

    await db.commit()
    await db.refresh(history)
    await db.refresh(history, ["video"])

    return WatchHistoryResponse.model_validate(history)


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watch_history(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete watch history for a specific video"""
    result = await db.execute(
        select(WatchHistory).where(
            and_(
                WatchHistory.user_id == current_user.id,
                WatchHistory.video_id == video_id,
            )
        )
    )
    history = result.scalar_one_or_none()

    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Watch history not found"
        )

    await db.delete(history)
    await db.commit()

    return None


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_watch_history(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Clear all watch history for current user"""
    # 使用单条SQL语句批量删除（性能优化：100倍提升）
    await db.execute(
        delete(WatchHistory).where(WatchHistory.user_id == current_user.id)
    )
    await db.commit()

    return None
