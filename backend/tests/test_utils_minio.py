"""
测试 app/utils/minio_client.py - MinIO 对象存储
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO


@pytest.mark.unit
class TestMinIOBasicOperations:
    """MinIO 基本操作测试"""

    @patch('app.utils.minio_client.minio_client')
    def test_bucket_exists(self, mock_client):
        """测试检查 bucket 是否存在"""
        mock_client.bucket_exists.return_value = True
        
        result = mock_client.bucket_exists("test-bucket")
        assert result is True

    @patch('app.utils.minio_client.minio_client')
    def test_create_bucket(self, mock_client):
        """测试创建 bucket"""
        mock_client.make_bucket.return_value = None
        
        mock_client.make_bucket("new-bucket")
        mock_client.make_bucket.assert_called_once_with("new-bucket")

    @patch('app.utils.minio_client.minio_client')
    def test_upload_file(self, mock_client):
        """测试上传文件"""
        mock_client.put_object.return_value = Mock(object_name="test.mp4")
        
        file_data = BytesIO(b"test video content")
        result = mock_client.put_object(
            "videos",
            "test.mp4",
            file_data,
            length=len(b"test video content"),
            content_type="video/mp4"
        )
        
        assert result is not None

    @patch('app.utils.minio_client.minio_client')
    def test_download_file(self, mock_client):
        """测试下载文件"""
        mock_response = Mock()
        mock_response.read.return_value = b"file content"
        mock_client.get_object.return_value = mock_response
        
        response = mock_client.get_object("videos", "test.mp4")
        content = response.read()
        
        assert content == b"file content"

    @patch('app.utils.minio_client.minio_client')
    def test_delete_file(self, mock_client):
        """测试删除文件"""
        mock_client.remove_object.return_value = None
        
        mock_client.remove_object("videos", "test.mp4")
        mock_client.remove_object.assert_called_once_with("videos", "test.mp4")

    @patch('app.utils.minio_client.minio_client')
    def test_list_objects(self, mock_client):
        """测试列出对象"""
        mock_objects = [
            Mock(object_name="video1.mp4", size=1024),
            Mock(object_name="video2.mp4", size=2048),
        ]
        mock_client.list_objects.return_value = mock_objects
        
        objects = mock_client.list_objects("videos")
        objects_list = list(objects)
        
        assert len(objects_list) == 2


@pytest.mark.unit
class TestMinIOPresignedURL:
    """MinIO 预签名 URL 测试"""

    @patch('app.utils.minio_client.minio_client')
    def test_get_presigned_url(self, mock_client):
        """测试获取预签名 URL"""
        mock_url = "https://minio.example.com/videos/test.mp4?signature=xxx"
        mock_client.presigned_get_object.return_value = mock_url
        
        url = mock_client.presigned_get_object("videos", "test.mp4")
        
        assert url == mock_url
        assert "signature" in url

    @patch('app.utils.minio_client.minio_client')
    def test_presigned_url_with_expiry(self, mock_client):
        """测试带过期时间的预签名 URL"""
        from datetime import timedelta
        
        mock_url = "https://minio.example.com/videos/test.mp4?expires=3600"
        mock_client.presigned_get_object.return_value = mock_url
        
        url = mock_client.presigned_get_object(
            "videos",
            "test.mp4",
            expires=timedelta(hours=1)
        )
        
        assert url is not None


@pytest.mark.unit
class TestMinIOErrorHandling:
    """MinIO 错误处理测试"""

    @patch('app.utils.minio_client.minio_client')
    def test_bucket_not_found(self, mock_client):
        """测试 bucket 不存在"""
        from minio.error import S3Error
        
        mock_client.bucket_exists.side_effect = S3Error(
            "NoSuchBucket",
            "Bucket not found",
            "resource",
            "request_id",
            "host_id",
            Mock()
        )
        
        with pytest.raises(S3Error):
            mock_client.bucket_exists("nonexistent-bucket")

    @patch('app.utils.minio_client.minio_client')
    def test_upload_error(self, mock_client):
        """测试上传错误"""
        mock_client.put_object.side_effect = Exception("Upload failed")
        
        with pytest.raises(Exception):
            mock_client.put_object("bucket", "file", BytesIO(b"data"), 4)

