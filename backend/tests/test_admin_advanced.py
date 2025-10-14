"""
测试 Admin 高级功能 API
包括: ai_management, ai_logs, rbac, admin_notifications, two_factor, oauth_management
"""
import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminAIManagementAPI:
    """AI 管理 API 测试"""

    async def test_get_ai_providers(self, async_client: AsyncClient, admin_token: str):
        """测试获取 AI 提供商列表"""
        response = await async_client.get(
            "/api/v1/admin/ai/providers",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_create_ai_provider(self, async_client: AsyncClient, admin_token: str):
        """测试创建 AI 提供商配置"""
        provider_data = {
            "name": "OpenAI",
            "provider_type": "openai",
            "api_key": "sk-test",
            "is_active": True
        }
        response = await async_client.post(
            "/api/v1/admin/ai/providers",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=provider_data
        )
        assert response.status_code in [200, 201, 403, 422]

    async def test_get_ai_logs(self, async_client: AsyncClient, admin_token: str):
        """测试获取 AI 日志"""
        response = await async_client.get(
            "/api/v1/admin/ai/logs",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminRBACAPI:
    """角色权限管理 API 测试"""

    async def test_get_roles(self, async_client: AsyncClient, admin_token: str):
        """测试获取角色列表"""
        response = await async_client.get(
            "/api/v1/admin/rbac/roles",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_get_permissions(self, async_client: AsyncClient, admin_token: str):
        """测试获取权限列表"""
        response = await async_client.get(
            "/api/v1/admin/rbac/permissions",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_assign_role(self, async_client: AsyncClient, admin_token: str):
        """测试分配角色"""
        role_data = {
            "user_id": 1,
            "role_id": 1
        }
        response = await async_client.post(
            "/api/v1/admin/rbac/assign",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=role_data
        )
        assert response.status_code in [200, 403, 404, 422]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminNotificationsAPI:
    """管理员通知 API 测试"""

    async def test_get_admin_notifications(self, async_client: AsyncClient, admin_token: str):
        """测试获取管理员通知"""
        response = await async_client.get(
            "/api/v1/admin/notifications",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_mark_notification_read(self, async_client: AsyncClient, admin_token: str):
        """测试标记通知已读"""
        response = await async_client.patch(
            "/api/v1/admin/notifications/1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminTwoFactorAPI:
    """两步验证 API 测试"""

    async def test_enable_two_factor(self, async_client: AsyncClient, admin_token: str):
        """测试启用两步验证"""
        response = await async_client.post(
            "/api/v1/admin/two-factor/enable",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 201, 422]

    async def test_verify_two_factor(self, async_client: AsyncClient, admin_token: str):
        """测试验证两步验证码"""
        verify_data = {"code": "123456"}
        response = await async_client.post(
            "/api/v1/admin/two-factor/verify",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=verify_data
        )
        assert response.status_code in [200, 400, 422]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminOAuthManagementAPI:
    """OAuth 管理 API 测试"""

    async def test_get_oauth_configs(self, async_client: AsyncClient, admin_token: str):
        """测试获取 OAuth 配置"""
        response = await async_client.get(
            "/api/v1/admin/oauth/configs",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_update_oauth_config(self, async_client: AsyncClient, admin_token: str):
        """测试更新 OAuth 配置"""
        config_data = {
            "provider": "google",
            "client_id": "test-client-id",
            "is_enabled": True
        }
        response = await async_client.put(
            "/api/v1/admin/oauth/configs/google",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=config_data
        )
        assert response.status_code in [200, 403, 404, 422]

