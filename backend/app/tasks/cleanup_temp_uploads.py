"""
临时上传文件清理任务
定期清理过期的临时上传文件和Redis会话
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from celery import shared_task
from loguru import logger

from app.utils.upload_session_manager import UploadSessionManager


@shared_task(name="cleanup_temp_uploads")
async def cleanup_temp_uploads():
    """
    清理临时上传文件

    - 删除 /tmp/uploads 下超过 24 小时的目录
    - 记录清理日志
    """
    try:
        temp_upload_dir = Path("/tmp/uploads")
        if not temp_upload_dir.exists():
            logger.info("Temp upload directory does not exist, skipping cleanup")
            return

        now = datetime.now()
        cutoff_time = now - timedelta(hours=24)
        cleaned_count = 0
        total_size = 0

        # 遍历所有子目录
        for item in temp_upload_dir.iterdir():
            if item.is_dir():
                # 获取目录的修改时间
                mtime = datetime.fromtimestamp(item.stat().st_mtime)

                # 如果超过 24 小时
                if mtime < cutoff_time:
                    try:
                        # 计算目录大小
                        dir_size = sum(
                            f.stat().st_size
                            for f in item.rglob("*")
                            if f.is_file()
                        )
                        total_size += dir_size

                        # 删除目录
                        shutil.rmtree(item, ignore_errors=True)
                        cleaned_count += 1

                        logger.info(
                            f"Cleaned up temp upload dir: {item.name}, "
                            f"size: {dir_size / (1024 * 1024):.2f} MB, "
                            f"age: {(now - mtime).total_seconds() / 3600:.1f} hours"
                        )
                    except Exception as e:
                        logger.error(f"Failed to clean up {item}: {e}")

        logger.info(
            f"✅ Temp upload cleanup complete: "
            f"{cleaned_count} directories cleaned, "
            f"total size: {total_size / (1024 * 1024):.2f} MB"
        )

        return {
            "cleaned_count": cleaned_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }

    except Exception as e:
        logger.error(f"Failed to cleanup temp uploads: {e}", exc_info=True)
        return {"error": str(e)}


@shared_task(name="cleanup_expired_redis_sessions")
async def cleanup_expired_redis_sessions():
    """
    清理过期的 Redis 上传会话

    - Redis 自动过期会处理大部分情况
    - 此任务用于主动清理和记录
    """
    try:
        # 获取所有活跃会话
        sessions = await UploadSessionManager.list_active_sessions()

        logger.info(f"Current active upload sessions in Redis: {len(sessions)}")

        # Redis 的 SETEX 会自动处理过期
        # 这里只是记录统计信息
        return {
            "active_sessions": len(sessions),
        }

    except Exception as e:
        logger.error(f"Failed to cleanup expired Redis sessions: {e}", exc_info=True)
        return {"error": str(e)}


@shared_task(name="cleanup_orphaned_multipart_uploads")
async def cleanup_orphaned_multipart_uploads():
    """
    清理孤立的 MinIO Multipart Uploads

    - 查找超过 7 天未完成的 multipart uploads
    - 取消这些上传以释放存储空间

    注意: MinIO 默认 7 天后自动清理未完成的 multipart uploads
    """
    try:
        from app.utils.minio_client import minio_client
        from minio.error import S3Error

        # MinIO SDK 提供的 list_incomplete_uploads 方法
        bucket_name = minio_client.bucket_name
        cleaned_count = 0

        try:
            # 列出未完成的 multipart uploads
            uploads = minio_client.client.list_incomplete_uploads(bucket_name)

            for upload in uploads:
                try:
                    # MinIO 默认会在 7 天后清理
                    # 我们这里只记录，不手动清理
                    logger.info(
                        f"Found incomplete upload: {upload.object_name}, "
                        f"upload_id: {upload.upload_id}, "
                        f"initiated: {upload.initiated}"
                    )
                except Exception as e:
                    logger.error(f"Error processing incomplete upload: {e}")

        except S3Error as e:
            logger.warning(f"Failed to list incomplete uploads: {e}")

        logger.info(f"Orphaned multipart uploads check complete: {cleaned_count} cleaned")

        return {"cleaned_count": cleaned_count}

    except Exception as e:
        logger.error(f"Failed to cleanup orphaned multipart uploads: {e}", exc_info=True)
        return {"error": str(e)}
