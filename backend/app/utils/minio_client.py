"""
MinIO 客户端工具
用于上传、下载和管理视频文件
"""
from minio import Minio
from minio.error import S3Error
from app.config import settings
import io
from typing import BinaryIO, Optional
from datetime import timedelta


class MinIOClient:
    """MinIO 客户端封装"""

    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = settings.MINIO_BUCKET
        self._ensure_bucket()

    def _ensure_bucket(self):
        """确保存储桶存在，不存在则创建"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                print(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            print(f"Error ensuring bucket: {e}")

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
            print(f"Error uploading video: {e}")
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

    def delete_subtitle(self, video_id: int, language: str, format: str = "vtt") -> bool:
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
            print(f"Error generating presigned URL: {e}")
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
            print(f"Error getting object size: {e}")
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
            print(f"Error deleting file: {e}")
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
            print(f"Error listing files: {e}")
            return []


# 创建全局实例
minio_client = MinIOClient()
