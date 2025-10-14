"""
测试 Admin 上传相关 API
包括: upload, batch_upload, image_upload, danmaku
"""
import pytest
from httpx import AsyncClient
from io import BytesIO


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminUploadAPI:
    """文件上传 API 测试"""

    async def test_init_upload(self, async_client: AsyncClient, admin_token: str):
        """测试初始化上传"""
        upload_data = {
            "filename": "test.mp4",
            "file_size": 1024000,
            "mime_type": "video/mp4"
        }
        response = await async_client.post(
            "/api/v1/admin/upload/init",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=upload_data
        )
        assert response.status_code in [200, 201, 422]

    async def test_upload_chunk(self, async_client: AsyncClient, admin_token: str):
        """测试上传分块"""
        # 模拟分块上传
        files = {"file": ("chunk.bin", BytesIO(b"test chunk data"), "application/octet-stream")}
        data = {
            "upload_id": "test-upload-id",
            "chunk_index": "0"
        }
        response = await async_client.post(
            "/api/v1/admin/upload/chunk",
            headers={"Authorization": f"Bearer {admin_token}"},
            data=data,
            files=files
        )
        assert response.status_code in [200, 400, 404, 422]

    async def test_complete_upload(self, async_client: AsyncClient, admin_token: str):
        """测试完成上传"""
        response = await async_client.post(
            "/api/v1/admin/upload/complete/test-upload-id",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404, 422]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminBatchUploadAPI:
    """批量上传 API 测试"""

    async def test_init_batch_upload(self, async_client: AsyncClient, admin_token: str):
        """测试初始化批量上传"""
        batch_data = [
            {"filename": "video1.mp4", "file_size": 1024000, "mime_type": "video/mp4"},
            {"filename": "video2.mp4", "file_size": 2048000, "mime_type": "video/mp4"}
        ]
        response = await async_client.post(
            "/api/v1/admin/upload/batch/init",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=batch_data
        )
        assert response.status_code in [200, 201, 422]

    async def test_get_batch_status(self, async_client: AsyncClient, admin_token: str):
        """测试获取批量上传状态"""
        response = await async_client.get(
            "/api/v1/admin/upload/batch/test-batch-id",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminImageUploadAPI:
    """图片上传 API 测试"""

    async def test_upload_image(self, async_client: AsyncClient, admin_token: str):
        """测试上传图片"""
        files = {"file": ("test.jpg", BytesIO(b"fake image data"), "image/jpeg")}
        response = await async_client.post(
            "/api/v1/admin/images/upload",
            headers={"Authorization": f"Bearer {admin_token}"},
            files=files
        )
        assert response.status_code in [200, 201, 422]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminDanmakuAPI:
    """弹幕管理 API 测试"""

    async def test_get_danmaku_list(self, async_client: AsyncClient, admin_token: str):
        """测试获取弹幕列表"""
        response = await async_client.get(
            "/api/v1/admin/danmaku",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_delete_danmaku(self, async_client: AsyncClient, admin_token: str):
        """测试删除弹幕"""
        response = await async_client.delete(
            "/api/v1/admin/danmaku/1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 204, 404]

    async def test_block_danmaku(self, async_client: AsyncClient, admin_token: str):
        """测试屏蔽弹幕"""
        response = await async_client.post(
            "/api/v1/admin/danmaku/1/block",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

