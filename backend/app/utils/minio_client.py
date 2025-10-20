"""
MinIO 客户端工具
用于上传、下载和管理视频文件

使用单例模式和延迟初始化，避免应用启动时阻塞
"""

import threading
from datetime import timedelta
from typing import BinaryIO, Optional

from loguru import logger
from minio import Minio
from minio.error import S3Error

from app.config import settings


class MinIOClient:
    """MinIO 客户端封装 - 单例模式 + 延迟初始化"""

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # 避免重复初始化
        if MinIOClient._initialized:
            return

        with MinIOClient._lock:
            if not MinIOClient._initialized:
                self._client = None
                self.bucket_name = settings.MINIO_BUCKET
                MinIOClient._initialized = True

    @property
    def client(self) -> Minio:
        """延迟初始化MinIO客户端"""
        if self._client is None:
            with MinIOClient._lock:
                if self._client is None:
                    self._client = Minio(
                        settings.MINIO_ENDPOINT,
                        access_key=settings.MINIO_ACCESS_KEY,
                        secret_key=settings.MINIO_SECRET_KEY,
                        secure=settings.MINIO_SECURE,
                    )
                    self._ensure_bucket()
        return self._client

    def _ensure_bucket(self):
        """确保存储桶存在，不存在则创建"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket: {e}", exc_info=True)

    def upload_video(
        self,
        file: BinaryIO,
        object_name: str,
        content_type: str = "video/mp4",
        metadata: Optional[dict] = None,
    ) -> str:
        """
        上传视频文件

        Args:
            file: 文件对象
            object_name: 对象名称（存储路径）
            content_type: 文件类型
            metadata: 元数据

        Returns:
            str: 文件访问 URL
        """
        try:
            # 获取文件大小
            file.seek(0, 2)  # 移动到文件末尾
            file_size = file.tell()
            file.seek(0)  # 移动回文件开头

            # 上传文件
            self.client.put_object(
                self.bucket_name,
                object_name,
                file,
                file_size,
                content_type=content_type,
                metadata=metadata or {},
            )

            # 返回文件 URL
            return f"{settings.MINIO_PUBLIC_URL}/{self.bucket_name}/{object_name}"

        except S3Error as e:
            logger.error(f"Error uploading video: {e}", exc_info=True)
            raise

    def upload_image(
        self,
        file: BinaryIO,
        object_name: str,
        content_type: str = "image/jpeg",
    ) -> str:
        """
        上传图片文件（封面、海报等）

        Args:
            file: 文件对象
            object_name: 对象名称
            content_type: 文件类型

        Returns:
            str: 文件访问 URL
        """
        return self.upload_video(file, object_name, content_type)

    def upload_file(
        self,
        file_content: bytes,
        object_name: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        通用文件上传方法（支持字节内容）

        Args:
            file_content: 文件字节内容
            object_name: 对象名称（存储路径）
            content_type: 文件类型

        Returns:
            str: 对象名称
        """
        from io import BytesIO

        try:
            file_size = len(file_content)
            file_obj = BytesIO(file_content)

            # 上传文件
            self.client.put_object(
                self.bucket_name,
                object_name,
                file_obj,
                file_size,
                content_type=content_type,
            )

            # 返回对象名称
            return object_name

        except S3Error as e:
            logger.error(f"Error uploading file: {e}", exc_info=True)
            raise

    def upload_subtitle(
        self,
        file: BinaryIO,
        video_id: int,
        language: str,
        format: str = "vtt",
    ) -> str:
        """
        上传字幕文件

        Args:
            file: 字幕文件对象
            video_id: 视频ID
            language: 语言代码 (zh-CN, en-US等)
            format: 字幕格式 (vtt, srt, ass)

        Returns:
            str: 字幕文件URL
        """
        object_name = f"subtitles/video_{video_id}_{language}.{format}"
        content_type = "text/vtt" if format == "vtt" else "text/plain"
        return self.upload_video(file, object_name, content_type)

    def upload_thumbnail(
        self,
        file: BinaryIO,
        video_id: int,
        thumbnail_type: str = "poster",
    ) -> str:
        """
        上传视频缩略图

        Args:
            file: 图片文件对象
            video_id: 视频ID
            thumbnail_type: 缩略图类型 (poster/preview/frame)

        Returns:
            str: 缩略图URL
        """
        object_name = f"thumbnails/video_{video_id}_{thumbnail_type}.jpg"
        return self.upload_image(file, object_name, "image/jpeg")

    def get_subtitle_url(
        self,
        video_id: int,
        language: str,
        format: str = "vtt",
        expires: timedelta = timedelta(days=7),
    ) -> str:
        """
        获取字幕文件的预签名URL

        Args:
            video_id: 视频ID
            language: 语言代码
            format: 字幕格式
            expires: 过期时间 (默认7天)

        Returns:
            str: 预签名URL
        """
        object_name = f"subtitles/video_{video_id}_{language}.{format}"
        return self.get_presigned_url(object_name, expires)

    def delete_subtitle(
        self, video_id: int, language: str, format: str = "vtt"
    ) -> bool:
        """
        删除字幕文件

        Args:
            video_id: 视频ID
            language: 语言代码
            format: 字幕格式

        Returns:
            bool: 是否成功删除
        """
        object_name = f"subtitles/video_{video_id}_{language}.{format}"
        return self.delete_file(object_name)

    def delete_thumbnail(self, video_id: int, thumbnail_type: str = "poster") -> bool:
        """
        删除缩略图

        Args:
            video_id: 视频ID
            thumbnail_type: 缩略图类型

        Returns:
            bool: 是否成功删除
        """
        object_name = f"thumbnails/video_{video_id}_{thumbnail_type}.jpg"
        return self.delete_file(object_name)

    def get_file_url(self, object_name: str) -> str:
        """
        获取文件的公共访问 URL

        Args:
            object_name: 对象名称

        Returns:
            str: 文件访问 URL
        """
        return f"{settings.MINIO_PUBLIC_URL}/{self.bucket_name}/{object_name}"

    def get_presigned_url(
        self,
        object_name: str,
        expires: timedelta = timedelta(hours=1),
    ) -> str:
        """
        获取预签名 URL（用于临时访问）

        Args:
            object_name: 对象名称
            expires: 过期时间

        Returns:
            str: 预签名 URL
        """
        try:
            url = self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=expires,
            )
            return url
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {e}", exc_info=True)
            raise

    def get_object_size(self, object_name: str) -> int:
        """
        获取对象文件大小

        Args:
            object_name: 对象名称

        Returns:
            int: 文件大小(字节)

        Raises:
            S3Error: 如果对象不存在或获取失败
        """
        try:
            stat = self.client.stat_object(self.bucket_name, object_name)
            return stat.size
        except S3Error as e:
            logger.error(f"Error getting object size: {e}", exc_info=True)
            raise

    def get_file(self, object_name: str) -> bytes:
        """
        获取文件内容（字节）

        Args:
            object_name: 对象名称

        Returns:
            bytes: 文件内容

        Raises:
            S3Error: 如果文件不存在或获取失败
        """
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error(f"Error getting file: {e}", exc_info=True)
            raise

    def delete_file(self, object_name: str) -> bool:
        """
        删除文件

        Args:
            object_name: 对象名称

        Returns:
            bool: 是否成功
        """
        try:
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            logger.error(f"Error deleting file: {e}", exc_info=True)
            return False

    def file_exists(self, object_name: str) -> bool:
        """
        检查文件是否存在

        Args:
            object_name: 对象名称

        Returns:
            bool: 是否存在
        """
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error:
            return False

    def list_files(self, prefix: str = "") -> list:
        """
        列出文件

        Args:
            prefix: 前缀过滤

        Returns:
            list: 文件列表
        """
        try:
            objects = self.client.list_objects(
                self.bucket_name,
                prefix=prefix,
                recursive=True,
            )
            return [obj.object_name for obj in objects]
        except S3Error as e:
            logger.error(f"Error listing files: {e}", exc_info=True)
            return []

    def get_bucket_usage(self) -> dict:
        """
        获取存储桶使用情况统计

        Returns:
            dict: 包含总大小、对象数量等信息
        """
        try:
            total_size = 0
            object_count = 0

            # 列出所有对象并累加大小
            objects = self.client.list_objects(
                self.bucket_name,
                recursive=True,
            )

            for obj in objects:
                total_size += obj.size
                object_count += 1

            # 转换为 GB
            total_size_gb = total_size / (1024 ** 3)

            return {
                "total_size_bytes": total_size,
                "total_size_gb": round(total_size_gb, 2),
                "object_count": object_count,
                "bucket_name": self.bucket_name
            }

        except S3Error as e:
            logger.error(f"Error getting bucket usage: {e}", exc_info=True)
            return {
                "total_size_bytes": 0,
                "total_size_gb": 0,
                "object_count": 0,
                "error": str(e)
            }

    def download_file(self, object_name: str, local_path: str) -> bool:
        """
        从MinIO下载文件到本地路径

        Args:
            object_name: MinIO对象名称（如 "videos/123/original.mp4"）
            local_path: 本地文件保存路径

        Returns:
            bool: 是否下载成功

        Raises:
            S3Error: 如果文件不存在或下载失败
        """
        try:
            self.client.fget_object(
                self.bucket_name,
                object_name,
                local_path,
            )
            logger.info(f"Downloaded {object_name} to {local_path}")
            return True
        except S3Error as e:
            logger.error(f"Error downloading file: {e}", exc_info=True)
            raise

    def upload_file_from_path(
        self,
        local_path: str,
        object_name: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        从本地路径上传文件到MinIO

        Args:
            local_path: 本地文件路径
            object_name: MinIO对象名称
            content_type: 文件MIME类型

        Returns:
            str: 对象名称

        Raises:
            S3Error: 如果上传失败
        """
        try:
            self.client.fput_object(
                self.bucket_name,
                object_name,
                local_path,
                content_type=content_type,
            )
            logger.info(f"Uploaded {local_path} to {object_name}")
            return object_name
        except S3Error as e:
            logger.error(f"Error uploading file from path: {e}", exc_info=True)
            raise

    # ========== Multipart Upload Methods ==========

    def create_multipart_upload(
        self,
        object_name: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[dict] = None,
    ) -> str:
        """
        创建 MinIO Multipart Upload

        Args:
            object_name: 对象名称
            content_type: 文件类型
            metadata: 元数据

        Returns:
            str: Upload ID

        Raises:
            S3Error: 如果创建失败
        """
        try:
            # MinIO Python SDK 使用底层 S3 API
            upload_id = self.client._create_multipart_upload(
                self.bucket_name, object_name, metadata or {}
            )
            logger.info(
                f"Created multipart upload: {upload_id} for object {object_name}"
            )
            return upload_id
        except S3Error as e:
            logger.error(f"Error creating multipart upload: {e}", exc_info=True)
            raise

    def upload_part(
        self,
        object_name: str,
        upload_id: str,
        part_number: int,
        data: bytes,
    ) -> str:
        """
        上传一个分片

        Args:
            object_name: 对象名称
            upload_id: Multipart Upload ID
            part_number: 分片编号（从 1 开始）
            data: 分片数据

        Returns:
            str: ETag

        Raises:
            S3Error: 如果上传失败
        """
        try:
            from io import BytesIO

            # 上传分片
            etag = self.client._upload_part(
                self.bucket_name,
                object_name,
                upload_id,
                part_number,
                BytesIO(data),
                len(data),
            )
            logger.debug(
                f"Uploaded part {part_number} for {object_name}, ETag: {etag}"
            )
            return etag
        except S3Error as e:
            logger.error(
                f"Error uploading part {part_number}: {e}", exc_info=True
            )
            raise

    def complete_multipart_upload(
        self,
        object_name: str,
        upload_id: str,
        parts: list,
    ) -> str:
        """
        完成 Multipart Upload

        Args:
            object_name: 对象名称
            upload_id: Upload ID
            parts: 分片列表 [(part_number, etag), ...]

        Returns:
            str: 文件 URL

        Raises:
            S3Error: 如果完成失败
        """
        try:
            # 完成上传
            self.client._complete_multipart_upload(
                self.bucket_name, object_name, upload_id, parts
            )
            logger.info(
                f"Completed multipart upload for {object_name}, total parts: {len(parts)}"
            )

            # 返回文件 URL
            return f"{settings.MINIO_PUBLIC_URL}/{self.bucket_name}/{object_name}"

        except S3Error as e:
            logger.error(f"Error completing multipart upload: {e}", exc_info=True)
            raise

    def abort_multipart_upload(
        self,
        object_name: str,
        upload_id: str,
    ) -> None:
        """
        取消 Multipart Upload

        Args:
            object_name: 对象名称
            upload_id: Upload ID

        Raises:
            S3Error: 如果取消失败
        """
        try:
            self.client._abort_multipart_upload(
                self.bucket_name, object_name, upload_id
            )
            logger.info(f"Aborted multipart upload: {upload_id} for {object_name}")
        except S3Error as e:
            logger.error(f"Error aborting multipart upload: {e}", exc_info=True)
            raise


# 创建全局实例
minio_client = MinIOClient()
