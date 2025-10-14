"""
批量操作API
为管理员提供批量处理功能，提高运营效率
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.comment import Comment, CommentStatus
from app.models.user import AdminUser
from app.models.video import Video, VideoStatus
from app.utils.cache import Cache
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


# Request schemas
class BatchVideoStatusUpdate(BaseModel):
    """批量更新视频状态"""

    video_ids: List[int]
    status: VideoStatus


class BatchCommentStatusUpdate(BaseModel):
    """批量更新评论状态"""

    comment_ids: List[int]
    status: CommentStatus


class BatchDeleteRequest(BaseModel):
    """批量删除请求"""

    ids: List[int]


# Video batch operations
@router.post("/videos/status")
async def batch_update_video_status(
    data: BatchVideoStatusUpdate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    批量更新视频状态

    - 最多支持100个视频
    - 返回更新数量
    - 自动清除相关缓存
    """
    if len(data.video_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 videos per batch operation",
        )

    if len(data.video_ids) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No video IDs provided"
        )

    # 使用单条SQL更新（性能优化）
    result = await db.execute(
        update(Video).where(Video.id.in_(data.video_ids)).values(status=data.status)
    )

    updated_count = result.rowcount
    await db.commit()

    # 清除相关缓存
    await Cache.delete_pattern("videos_list:*")
    await Cache.delete_pattern("trending_videos:*")
    await Cache.delete_pattern("featured_videos:*")
    await Cache.delete_pattern("recommended_videos:*")

    # 清除单个视频缓存
    for video_id in data.video_ids:
        await Cache.delete(f"video_detail:{video_id}")

    logger.info(
        f"Batch updated video status: {updated_count} videos to {data.status}",
        extra={"admin_id": current_admin.id, "video_ids": data.video_ids[:10]},
    )

    # 🆕 发送批量操作通知
    if updated_count > 0:
        try:
            from app.utils.admin_notification_service import AdminNotificationService

            await AdminNotificationService.notify_batch_operation(
                db=db,
                operation_type="update",
                entity_type="video",
                count=updated_count,
                admin_username=current_admin.username,
                details=f"状态更新为 {data.status}",
            )
        except Exception as e:
            logger.error(f"Failed to send batch operation notification: {e}")

    return {
        "success": True,
        "updated": updated_count,
        "message": f"Successfully updated {updated_count} videos to {data.status}",
    }


@router.post("/videos/delete")
async def batch_delete_videos(
    data: BatchDeleteRequest,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    批量删除视频

    - 最多支持50个视频（删除操作更谨慎）
    - 仅删除数据库记录（MinIO文件需单独处理）
    - 返回删除数量
    """
    if len(data.ids) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 videos per batch delete operation",
        )

    if len(data.ids) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No video IDs provided"
        )

    # 使用单条SQL删除（性能优化）
    result = await db.execute(delete(Video).where(Video.id.in_(data.ids)))

    deleted_count = result.rowcount
    await db.commit()

    # 清除相关缓存
    await Cache.delete_pattern("videos_list:*")
    for video_id in data.ids:
        await Cache.delete(f"video_detail:{video_id}")

    logger.warning(
        f"Batch deleted videos: {deleted_count} videos",
        extra={"admin_id": current_admin.id, "video_ids": data.ids[:10]},
    )

    # 🆕 发送批量删除通知
    if deleted_count > 0:
        try:
            from app.utils.admin_notification_service import AdminNotificationService

            await AdminNotificationService.notify_batch_operation(
                db=db,
                operation_type="delete",
                entity_type="video",
                count=deleted_count,
                admin_username=current_admin.username,
            )
        except Exception as e:
            logger.error(f"Failed to send batch delete notification: {e}")

    return {
        "success": True,
        "deleted": deleted_count,
        "message": f"Successfully deleted {deleted_count} videos",
        "warning": "MinIO files need to be cleaned up separately",
    }


# Comment batch operations
@router.post("/comments/status")
async def batch_update_comment_status(
    data: BatchCommentStatusUpdate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    批量审核评论

    - 最多支持100个评论
    - 支持批准、拒绝、待审核状态
    - 自动清除评论缓存
    """
    if len(data.comment_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 comments per batch operation",
        )

    if len(data.comment_ids) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No comment IDs provided"
        )

    # 使用单条SQL更新
    result = await db.execute(
        update(Comment)
        .where(Comment.id.in_(data.comment_ids))
        .values(status=data.status)
    )

    updated_count = result.rowcount
    await db.commit()

    # 清除评论缓存
    await Cache.delete_pattern("video_comments:*")

    logger.info(
        f"Batch updated comment status: {updated_count} comments to {data.status}",
        extra={"admin_id": current_admin.id, "comment_ids": data.comment_ids[:10]},
    )

    return {
        "success": True,
        "updated": updated_count,
        "message": f"Successfully updated {updated_count} comments to {data.status}",
    }


@router.post("/comments/delete")
async def batch_delete_comments(
    data: BatchDeleteRequest,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    批量删除评论

    - 最多支持100个评论
    - 级联删除回复
    - 自动更新视频评论计数
    """
    if len(data.ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 comments per batch delete operation",
        )

    if len(data.ids) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No comment IDs provided"
        )

    # 使用单条SQL删除
    result = await db.execute(delete(Comment).where(Comment.id.in_(data.ids)))

    deleted_count = result.rowcount
    await db.commit()

    # 清除评论缓存
    await Cache.delete_pattern("video_comments:*")

    logger.warning(
        f"Batch deleted comments: {deleted_count} comments",
        extra={"admin_id": current_admin.id, "comment_ids": data.ids[:10]},
    )

    return {
        "success": True,
        "deleted": deleted_count,
        "message": f"Successfully deleted {deleted_count} comments",
    }


# Cache operations
@router.post("/cache/clear")
async def clear_cache_pattern(
    pattern: str,
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    清除缓存（按模式）

    支持的模式：
    - videos_list:* - 视频列表缓存
    - video_detail:* - 视频详情缓存
    - video_comments:* - 评论缓存
    - admin:stats:* - 统计缓存
    - * - 清除所有（慎用）
    """
    allowed_patterns = [
        "videos_list:*",
        "video_detail:*",
        "video_comments:*",
        "trending_videos:*",
        "featured_videos:*",
        "recommended_videos:*",
        "admin:stats:*",
        "search_results:*",
    ]

    # 安全检查
    if pattern not in allowed_patterns and pattern != "*":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid pattern. Allowed patterns: {', '.join(allowed_patterns)} or '*'",
        )

    # 清除缓存
    if pattern == "*":
        # 清除所有缓存（需要确认）
        from app.utils.cache import get_redis

        redis_client = await get_redis()
        await redis_client.flushdb()
        deleted_count = "all"
    else:
        deleted_count = await Cache.delete_pattern(pattern)

    logger.info(
        f"Cache cleared: {pattern}",
        extra={"admin_id": current_admin.id, "pattern": pattern, "deleted": deleted_count},
    )

    return {
        "success": True,
        "pattern": pattern,
        "deleted": deleted_count,
        "message": f"Successfully cleared cache matching '{pattern}'",
    }
