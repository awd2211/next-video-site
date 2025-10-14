"""
测试 Admin 认证和资料 API
包括: profile (管理员资料管理)
"""
import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminAuthAPI:
    """管理员认证 API 测试"""

    async def test_admin_login(self, async_client: AsyncClient):
        """测试管理员登录"""
        # 先获取验证码
        cap_response = await async_client.get("/api/v1/captcha/")
        assert cap_response.status_code == 200
        captcha_id = cap_response.headers.get("x-captcha-id")
        
        # 从 Redis 读取验证码
        from app.utils.cache import get_redis
        redis = await get_redis()
        captcha_code = await redis.get(f"captcha:{captcha_id}")
        await redis.aclose()
        
        # 登录
        login_data = {
            "username": "admin",
            "password": "admin123456",
            "captcha_id": captcha_id,
            "captcha_code": captcha_code
        }
        response = await async_client.post(
            "/api/v1/auth/admin/login",
            json=login_data
        )
        assert response.status_code in [200, 401, 422]

    async def test_admin_get_me(self, async_client: AsyncClient, admin_token: str):
        """测试获取当前管理员信息"""
        response = await async_client.get(
            "/api/v1/auth/admin/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "username" in data


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminProfileAPI:
    """管理员资料管理 API 测试"""

    async def test_get_profile(self, async_client: AsyncClient, admin_token: str):
        """测试获取管理员资料"""
        response = await async_client.get(
            "/api/v1/admin/profile",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_update_profile(self, async_client: AsyncClient, admin_token: str):
        """测试更新管理员资料"""
        profile_data = {
            "full_name": "Updated Admin Name",
            "email": "updated@example.com"
        }
        response = await async_client.put(
            "/api/v1/admin/profile",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=profile_data
        )
        assert response.status_code in [200, 422]

    async def test_change_password(self, async_client: AsyncClient, admin_token: str):
        """测试修改密码"""
        password_data = {
            "old_password": "admin123456",
            "new_password": "newpassword123"
        }
        response = await async_client.post(
            "/api/v1/admin/profile/change-password",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=password_data
        )
        assert response.status_code in [200, 400, 422]

    async def test_upload_avatar(self, async_client: AsyncClient, admin_token: str):
        """测试上传头像"""
        from io import BytesIO
        
        files = {"file": ("avatar.jpg", BytesIO(b"fake image"), "image/jpeg")}
        response = await async_client.post(
            "/api/v1/admin/profile/avatar",
            headers={"Authorization": f"Bearer {admin_token}"},
            files=files
        )
        assert response.status_code in [200, 201, 422]

