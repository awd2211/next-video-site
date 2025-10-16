"""
上传会话管理器 - 使用 Redis 存储上传会话
支持分布式部署和断点续传
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from loguru import logger

from app.utils.cache import get_redis


class UploadSessionManager:
    """上传会话管理器 - 基于 Redis"""

    # Redis key 前缀
    SESSION_PREFIX = "upload_session:"
    # 会话过期时间（2小时）
    SESSION_TTL = 7200

    @staticmethod
    async def create_session(
        upload_id: str,
        filename: str,
        file_size: int,
        file_type: str,
        total_chunks: int,
        admin_id: int,
    ) -> Dict:
        """
        创建上传会话

        Args:
            upload_id: 上传会话ID
            filename: 文件名
            file_size: 文件大小（字节）
            file_type: 文件类型
            total_chunks: 总分片数
            admin_id: 管理员ID

        Returns:
            会话数据
        """
        try:
            client = await get_redis()
            key = f"{UploadSessionManager.SESSION_PREFIX}{upload_id}"

            session_data = {
                "upload_id": upload_id,
                "filename": filename,
                "file_size": file_size,
                "file_type": file_type,
                "total_chunks": total_chunks,
                "uploaded_chunks": [],
                "admin_id": admin_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "minio_upload_id": None,  # MinIO multipart upload ID
                "object_name": None,  # MinIO object name
            }

            # 存储到 Redis（使用 JSON 序列化）
            await client.setex(
                key, UploadSessionManager.SESSION_TTL, json.dumps(session_data)
            )

            logger.info(
                f"Created upload session: {upload_id} for file {filename} ({file_size} bytes)"
            )
            return session_data

        except Exception as e:
            logger.error(f"Failed to create upload session: {e}", exc_info=True)
            raise

    @staticmethod
    async def get_session(upload_id: str) -> Optional[Dict]:
        """
        获取上传会话

        Args:
            upload_id: 上传会话ID

        Returns:
            会话数据，不存在返回 None
        """
        try:
            client = await get_redis()
            key = f"{UploadSessionManager.SESSION_PREFIX}{upload_id}"

            data = await client.get(key)
            if not data:
                return None

            return json.loads(data)

        except Exception as e:
            logger.error(f"Failed to get upload session: {e}", exc_info=True)
            return None

    @staticmethod
    async def update_session(upload_id: str, updates: Dict) -> bool:
        """
        更新上传会话

        Args:
            upload_id: 上传会话ID
            updates: 要更新的字段

        Returns:
            是否成功
        """
        try:
            client = await get_redis()
            key = f"{UploadSessionManager.SESSION_PREFIX}{upload_id}"

            # 获取现有会话
            session = await UploadSessionManager.get_session(upload_id)
            if not session:
                logger.warning(f"Upload session not found: {upload_id}")
                return False

            # 更新字段
            session.update(updates)

            # 保存回 Redis（保持原有 TTL）
            ttl = await client.ttl(key)
            if ttl > 0:
                await client.setex(key, ttl, json.dumps(session))
            else:
                # 如果原 TTL 已过期，使用默认 TTL
                await client.setex(
                    key, UploadSessionManager.SESSION_TTL, json.dumps(session)
                )

            return True

        except Exception as e:
            logger.error(f"Failed to update upload session: {e}", exc_info=True)
            return False

    @staticmethod
    async def mark_chunk_uploaded(upload_id: str, chunk_index: int) -> bool:
        """
        标记分片为已上传

        Args:
            upload_id: 上传会话ID
            chunk_index: 分片索引

        Returns:
            是否成功
        """
        try:
            session = await UploadSessionManager.get_session(upload_id)
            if not session:
                return False

            uploaded_chunks: List[int] = session.get("uploaded_chunks", [])
            if chunk_index not in uploaded_chunks:
                uploaded_chunks.append(chunk_index)
                uploaded_chunks.sort()

            return await UploadSessionManager.update_session(
                upload_id, {"uploaded_chunks": uploaded_chunks}
            )

        except Exception as e:
            logger.error(f"Failed to mark chunk uploaded: {e}", exc_info=True)
            return False

    @staticmethod
    async def is_upload_complete(upload_id: str) -> bool:
        """
        检查上传是否完成

        Args:
            upload_id: 上传会话ID

        Returns:
            是否完成
        """
        try:
            session = await UploadSessionManager.get_session(upload_id)
            if not session:
                return False

            uploaded_chunks = session.get("uploaded_chunks", [])
            total_chunks = session.get("total_chunks", 0)

            return len(uploaded_chunks) == total_chunks

        except Exception as e:
            logger.error(f"Failed to check upload complete: {e}", exc_info=True)
            return False

    @staticmethod
    async def get_progress(upload_id: str) -> float:
        """
        获取上传进度

        Args:
            upload_id: 上传会话ID

        Returns:
            进度百分比（0-100）
        """
        try:
            session = await UploadSessionManager.get_session(upload_id)
            if not session:
                return 0.0

            uploaded_chunks = session.get("uploaded_chunks", [])
            total_chunks = session.get("total_chunks", 1)  # 避免除以0

            return (len(uploaded_chunks) / total_chunks) * 100

        except Exception as e:
            logger.error(f"Failed to get upload progress: {e}", exc_info=True)
            return 0.0

    @staticmethod
    async def delete_session(upload_id: str) -> bool:
        """
        删除上传会话

        Args:
            upload_id: 上传会话ID

        Returns:
            是否成功
        """
        try:
            client = await get_redis()
            key = f"{UploadSessionManager.SESSION_PREFIX}{upload_id}"

            await client.delete(key)
            logger.info(f"Deleted upload session: {upload_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete upload session: {e}", exc_info=True)
            return False

    @staticmethod
    async def extend_ttl(upload_id: str, seconds: int = None) -> bool:
        """
        延长会话过期时间

        Args:
            upload_id: 上传会话ID
            seconds: 延长的秒数，默认使用 SESSION_TTL

        Returns:
            是否成功
        """
        try:
            client = await get_redis()
            key = f"{UploadSessionManager.SESSION_PREFIX}{upload_id}"

            if seconds is None:
                seconds = UploadSessionManager.SESSION_TTL

            await client.expire(key, seconds)
            return True

        except Exception as e:
            logger.error(f"Failed to extend TTL: {e}", exc_info=True)
            return False

    @staticmethod
    async def list_active_sessions(admin_id: Optional[int] = None) -> List[Dict]:
        """
        列出活跃的上传会话

        Args:
            admin_id: 管理员ID，None 表示所有管理员

        Returns:
            会话列表
        """
        try:
            client = await get_redis()
            pattern = f"{UploadSessionManager.SESSION_PREFIX}*"

            sessions = []
            async for key in client.scan_iter(match=pattern):
                data = await client.get(key)
                if data:
                    session = json.loads(data)
                    # 如果指定了 admin_id，过滤
                    if admin_id is None or session.get("admin_id") == admin_id:
                        sessions.append(session)

            return sessions

        except Exception as e:
            logger.error(f"Failed to list active sessions: {e}", exc_info=True)
            return []

    @staticmethod
    async def cleanup_expired_sessions() -> int:
        """
        清理过期的会话（Redis 会自动过期，此方法用于主动清理）

        Returns:
            清理的会话数量
        """
        try:
            # Redis 的 SETEX 会自动处理过期，这里只是记录日志
            sessions = await UploadSessionManager.list_active_sessions()
            logger.info(
                f"Current active upload sessions: {len(sessions)}"
            )
            return 0

        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}", exc_info=True)
            return 0
