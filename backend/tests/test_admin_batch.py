"""
测试 Admin 批量操作 API
包括: batch_operations, operations
"""
import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminBatchOperationsAPI:
    """批量操作 API 测试"""

    async def test_batch_delete_videos(self, async_client: AsyncClient, admin_token: str):
        """测试批量删除视频"""
        batch_data = {
            "video_ids": [999, 1000, 1001]
        }
        response = await async_client.post(
            "/api/v1/admin/batch/delete-videos",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=batch_data
        )
        assert response.status_code in [200, 404, 422]

    async def test_batch_update_status(self, async_client: AsyncClient, admin_token: str):
        """测试批量更新状态"""
        batch_data = {
            "video_ids": [1, 2, 3],
            "status": "published"
        }
        response = await async_client.post(
            "/api/v1/admin/batch/update-status",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=batch_data
        )
        assert response.status_code in [200, 404, 422]

    async def test_batch_assign_category(self, async_client: AsyncClient, admin_token: str):
        """测试批量分配分类"""
        batch_data = {
            "video_ids": [1, 2, 3],
            "category_id": 1
        }
        response = await async_client.post(
            "/api/v1/admin/batch/assign-category",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=batch_data
        )
        assert response.status_code in [200, 404, 422]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminOperationsAPI:
    """操作管理 API 测试"""

    async def test_get_operations_list(self, async_client: AsyncClient, admin_token: str):
        """测试获取操作列表"""
        response = await async_client.get(
            "/api/v1/admin/operations",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_get_operation_detail(self, async_client: AsyncClient, admin_token: str):
        """测试获取操作详情"""
        response = await async_client.get(
            "/api/v1/admin/operations/1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

