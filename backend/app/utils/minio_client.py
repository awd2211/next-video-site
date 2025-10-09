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
