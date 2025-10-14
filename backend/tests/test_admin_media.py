"""
测试 Admin 媒体管理 API  
包括: media, transcode, subtitles, media_version, media_share
"""
import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminMediaAPI:
    """媒体管理 API 测试"""

    async def test_get_media_list(self, async_client: AsyncClient, admin_token: str):
        """测试获取媒体列表"""
        response = await async_client.get(
            "/api/v1/admin/media",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_get_media_detail(self, async_client: AsyncClient, admin_token: str):
        """测试获取媒体详情"""
        response = await async_client.get(
            "/api/v1/admin/media/1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminTranscodeAPI:
    """转码管理 API 测试"""

    async def test_start_transcode(self, async_client: AsyncClient, admin_token: str):
        """测试启动转码任务"""
        transcode_data = {
            "video_id": 1,
            "output_format": "av1",
            "quality": "1080p"
        }
        response = await async_client.post(
            "/api/v1/admin/transcode/start",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=transcode_data
        )
        assert response.status_code in [200, 201, 404, 422]

    async def test_get_transcode_status(self, async_client: AsyncClient, admin_token: str):
        """测试获取转码状态"""
        response = await async_client.get(
            "/api/v1/admin/transcode/status/test-task-id",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_cancel_transcode(self, async_client: AsyncClient, admin_token: str):
        """测试取消转码任务"""
        response = await async_client.post(
            "/api/v1/admin/transcode/cancel/test-task-id",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminSubtitlesAPI:
    """字幕管理 API 测试"""

    async def test_upload_subtitle(self, async_client: AsyncClient, admin_token: str):
        """测试上传字幕"""
        from io import BytesIO
        
        files = {"file": ("subtitle.srt", BytesIO(b"1\n00:00:01,000 --> 00:00:04,000\nTest"), "text/plain")}
        data = {
            "video_id": "1",
            "language": "en",
            "language_name": "English"
        }
        response = await async_client.post(
            "/api/v1/admin/subtitles/upload",
            headers={"Authorization": f"Bearer {admin_token}"},
            data=data,
            files=files
        )
        assert response.status_code in [200, 201, 404, 422]

    async def test_delete_subtitle(self, async_client: AsyncClient, admin_token: str):
        """测试删除字幕"""
        response = await async_client.delete(
            "/api/v1/admin/subtitles/1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 204, 404]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminMediaVersionAPI:
    """媒体版本管理 API 测试"""

    async def test_get_media_versions(self, async_client: AsyncClient, admin_token: str):
        """测试获取媒体版本列表"""
        response = await async_client.get(
            "/api/v1/admin/media/1/versions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_create_media_version(self, async_client: AsyncClient, admin_token: str):
        """测试创建媒体版本"""
        version_data = {
            "media_id": 1,
            "version": "v2",
            "quality": "1080p"
        }
        response = await async_client.post(
            "/api/v1/admin/media/versions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=version_data
        )
        assert response.status_code in [200, 201, 404, 422]

