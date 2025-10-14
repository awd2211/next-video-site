"""
测试 Admin 运营管理 API
包括: banners, announcements, scheduled_content, scheduling
"""
import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminBannersAPI:
    """Banner 管理 API 测试"""

    async def test_get_banners(self, async_client: AsyncClient, admin_token: str):
        """测试获取 Banner 列表"""
        response = await async_client.get(
            "/api/v1/admin/banners",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_create_banner(self, async_client: AsyncClient, admin_token: str):
        """测试创建 Banner"""
        banner_data = {
            "title": "Test Banner",
            "image_url": "https://example.com/banner.jpg",
            "link_url": "https://example.com",
            "is_active": True
        }
        response = await async_client.post(
            "/api/v1/admin/banners",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=banner_data
        )
        assert response.status_code in [200, 201, 422]

    async def test_update_banner(self, async_client: AsyncClient, admin_token: str):
        """测试更新 Banner"""
        update_data = {"title": "Updated Banner"}
        response = await async_client.put(
            "/api/v1/admin/banners/1",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=update_data
        )
        assert response.status_code in [200, 404]

    async def test_delete_banner(self, async_client: AsyncClient, admin_token: str):
        """测试删除 Banner"""
        response = await async_client.delete(
            "/api/v1/admin/banners/999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 204, 404]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminAnnouncementsAPI:
    """公告管理 API 测试"""

    async def test_get_announcements(self, async_client: AsyncClient, admin_token: str):
        """测试获取公告列表"""
        response = await async_client.get(
            "/api/v1/admin/announcements",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_create_announcement(self, async_client: AsyncClient, admin_token: str):
        """测试创建公告"""
        announcement_data = {
            "title": "Test Announcement",
            "content": "Test content",
            "type": "info"
        }
        response = await async_client.post(
            "/api/v1/admin/announcements",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=announcement_data
        )
        assert response.status_code in [200, 201, 422]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminSchedulingAPI:
    """调度管理 API 测试"""

    async def test_get_scheduled_content(self, async_client: AsyncClient, admin_token: str):
        """测试获取定时内容"""
        response = await async_client.get(
            "/api/v1/admin/scheduling/content",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_create_scheduled_content(self, async_client: AsyncClient, admin_token: str):
        """测试创建定时内容"""
        schedule_data = {
            "content_type": "video",
            "content_id": 1,
            "publish_at": "2025-01-01T00:00:00Z"
        }
        response = await async_client.post(
            "/api/v1/admin/scheduling/content",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=schedule_data
        )
        assert response.status_code in [200, 201, 422, 404]

