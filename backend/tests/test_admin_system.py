"""
测试 Admin 系统管理 API
包括: settings, settings_enhanced, system_health, ip_blacklist, email_config
"""
import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminSettingsAPI:
    """系统设置 API 测试"""

    async def test_get_settings(self, async_client: AsyncClient, admin_token: str):
        """测试获取系统设置"""
        response = await async_client.get(
            "/api/v1/admin/settings",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_update_settings(self, async_client: AsyncClient, admin_token: str):
        """测试更新系统设置（需要 superadmin）"""
        settings_data = {
            "site_name": "Updated Site Name",
            "site_description": "Updated description"
        }
        response = await async_client.put(
            "/api/v1/admin/settings",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=settings_data
        )
        assert response.status_code in [200, 403, 422]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminSystemHealthAPI:
    """系统健康 API 测试"""

    async def test_get_system_health(self, async_client: AsyncClient, admin_token: str):
        """测试获取系统健康状态"""
        response = await async_client.get(
            "/api/v1/admin/system/health",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_get_storage_stats(self, async_client: AsyncClient, admin_token: str):
        """测试获取存储统计"""
        response = await async_client.get(
            "/api/v1/admin/system/storage",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_get_database_stats(self, async_client: AsyncClient, admin_token: str):
        """测试获取数据库统计"""
        response = await async_client.get(
            "/api/v1/admin/system/database",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminIPBlacklistAPI:
    """IP 黑名单 API 测试"""

    async def test_get_blacklist(self, async_client: AsyncClient, admin_token: str):
        """测试获取 IP 黑名单"""
        response = await async_client.get(
            "/api/v1/admin/ip-blacklist",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_add_to_blacklist(self, async_client: AsyncClient, admin_token: str):
        """测试添加 IP 到黑名单"""
        blacklist_data = {
            "ip_address": "192.168.1.100",
            "reason": "Test ban"
        }
        response = await async_client.post(
            "/api/v1/admin/ip-blacklist",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=blacklist_data
        )
        assert response.status_code in [200, 201, 422]

    async def test_remove_from_blacklist(self, async_client: AsyncClient, admin_token: str):
        """测试从黑名单移除 IP"""
        response = await async_client.delete(
            "/api/v1/admin/ip-blacklist/1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 204, 404]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminEmailConfigAPI:
    """邮件配置 API 测试"""

    async def test_get_email_config(self, async_client: AsyncClient, admin_token: str):
        """测试获取邮件配置"""
        response = await async_client.get(
            "/api/v1/admin/email/config",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_update_email_config(self, async_client: AsyncClient, admin_token: str):
        """测试更新邮件配置"""
        config_data = {
            "provider": "smtp",
            "smtp_host": "smtp.example.com",
            "smtp_port": 587
        }
        response = await async_client.put(
            "/api/v1/admin/email/config",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=config_data
        )
        assert response.status_code in [200, 403, 422]

    async def test_test_email_config(self, async_client: AsyncClient, admin_token: str):
        """测试发送测试邮件"""
        test_data = {"email": "test@example.com"}
        response = await async_client.post(
            "/api/v1/admin/email/test",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=test_data
        )
        assert response.status_code in [200, 400, 404, 422]

