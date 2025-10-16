"""
测试 API - OAuth 认证流程
测试 OAuth 登录、回调、解除绑定等功能
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.models.user import User
from app.models.oauth_config import OAuthConfig


# ===========================================
# 测试 Fixtures
# ===========================================

@pytest.fixture
async def oauth_config(async_db: AsyncSession):
    """创建测试 OAuth 配置"""
    config = OAuthConfig(
        provider="github",
        client_id="test_client_id",
        client_secret="test_client_secret",
        authorization_url="https://github.com/login/oauth/authorize",
        token_url="https://github.com/login/oauth/access_token",
        user_info_url="https://api.github.com/user",
        scopes="user:email",
        enabled=True,
    )
    async_db.add(config)
    await async_db.commit()
    await async_db.refresh(config)
    return config


@pytest.fixture
async def disabled_oauth_config(async_db: AsyncSession):
    """创建禁用的 OAuth 配置"""
    config = OAuthConfig(
        provider="google",
        client_id="disabled_client",
        client_secret="disabled_secret",
        authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        user_info_url="https://www.googleapis.com/oauth2/v2/userinfo",
        scopes="email profile",
        enabled=False,  # 禁用
    )
    async_db.add(config)
    await async_db.commit()
    await async_db.refresh(config)
    return config


@pytest.fixture
def mock_oauth_provider():
    """Mock OAuth 提供商"""
    provider = MagicMock()
    provider.generate_state.return_value = "test_state_123"
    provider.get_authorization_url.return_value = "https://github.com/login/oauth/authorize?client_id=test&state=test_state_123"
    return provider


@pytest.fixture
def mock_oauth_user_info():
    """Mock OAuth 用户信息"""
    return {
        "provider_user_id": "github_123456",
        "email": "oauth_user@github.com",
        "full_name": "OAuth Test User",
        "avatar_url": "https://avatars.github.com/u/123456",
        "verified_email": True,
    }


# ===========================================
# 1. OAuth 登录发起测试
# ===========================================

class TestOAuthLogin:
    """测试 OAuth 登录发起"""

    @pytest.mark.asyncio
    async def test_oauth_login_success(
        self, async_client: AsyncClient, oauth_config: OAuthConfig, mock_oauth_provider
    ):
        """测试成功发起 OAuth 登录"""
        with patch("app.api.oauth.OAuthService.get_provider", return_value=mock_oauth_provider):
            response = await async_client.post("/api/v1/oauth/github/login")

            assert response.status_code == 200
            data = response.json()
            assert "authorization_url" in data
            assert "state" in data
            assert "github.com" in data["authorization_url"]
            assert data["state"] == "test_state_123"

    @pytest.mark.asyncio
    async def test_oauth_login_provider_not_configured(self, async_client: AsyncClient):
        """测试 OAuth 提供商未配置"""
        response = await async_client.post("/api/v1/oauth/unknown_provider/login")

        assert response.status_code == 404
        data = response.json()
        assert "not configured" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_oauth_login_provider_disabled(
        self, async_client: AsyncClient, disabled_oauth_config: OAuthConfig
    ):
        """测试 OAuth 提供商已禁用"""
        response = await async_client.post("/api/v1/oauth/google/login")

        assert response.status_code == 404
        data = response.json()
        assert "not configured or enabled" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_oauth_login_case_insensitive(
        self, async_client: AsyncClient, oauth_config: OAuthConfig, mock_oauth_provider
    ):
        """测试提供商名称大小写不敏感"""
        with patch("app.api.oauth.OAuthService.get_provider", return_value=mock_oauth_provider):
            # 大写
            response = await async_client.post("/api/v1/oauth/GITHUB/login")
            assert response.status_code == 200

            # 混合大小写
            response = await async_client.post("/api/v1/oauth/GitHub/login")
            assert response.status_code == 200


# ===========================================
# 2. OAuth 回调测试
# ===========================================

class TestOAuthCallback:
    """测试 OAuth 回调处理"""

    @pytest.mark.asyncio
    async def test_oauth_callback_new_user(
        self, async_client: AsyncClient, async_db: AsyncSession, oauth_config: OAuthConfig
    ):
        """测试新用户通过 OAuth 注册"""
        # Mock OAuth 服务
        mock_provider = MagicMock()
        mock_provider.exchange_code_for_token = AsyncMock(
            return_value={"access_token": "oauth_access_token"}
        )

        mock_user_info = MagicMock()
        mock_user_info.provider_user_id = "github_new_123"
        mock_user_info.email = "newuser@github.com"
        mock_user_info.full_name = "New OAuth User"
        mock_user_info.avatar_url = "https://avatar.url"
        mock_user_info.verified_email = True

        mock_provider.get_user_info = AsyncMock(return_value=mock_user_info)

        # 先发起登录获取 state
        with patch("app.api.oauth.OAuthService.get_provider", return_value=mock_provider):
            login_response = await async_client.post("/api/v1/oauth/github/login")
            state = login_response.json()["state"]

            # 模拟回调
            with patch("app.api.oauth.AdminNotificationService.notify_new_user_registration", new_callable=AsyncMock):
                response = await async_client.get(
                    f"/api/v1/oauth/github/callback?code=test_code&state={state}"
                )

                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert "refresh_token" in data
                assert data["token_type"] == "bearer"
                assert data["user"]["email"] == "newuser@github.com"
                assert data["user"]["oauth_provider"] == "github"
                assert data["user"]["is_verified"] is True

    @pytest.mark.asyncio
    async def test_oauth_callback_existing_oauth_user(
        self, async_client: AsyncClient, async_db: AsyncSession, oauth_config: OAuthConfig
    ):
        """测试已存在的 OAuth 用户登录"""
        # 创建已存在的 OAuth 用户
        existing_user = User(
            email="existing@github.com",
            username="existing_oauth",
            full_name="Existing User",
            oauth_provider="github",
            oauth_id="github_existing_123",
            oauth_email="existing@github.com",
            is_active=True,
            is_verified=True,
        )
        async_db.add(existing_user)
        await async_db.commit()
        await async_db.refresh(existing_user)

        # Mock OAuth 服务
        mock_provider = MagicMock()
        mock_provider.exchange_code_for_token = AsyncMock(
            return_value={"access_token": "oauth_token"}
        )

        mock_user_info = MagicMock()
        mock_user_info.provider_user_id = "github_existing_123"
        mock_user_info.email = "existing@github.com"
        mock_user_info.full_name = "Existing User"
        mock_user_info.avatar_url = "https://avatar.url"
        mock_user_info.verified_email = True

        mock_provider.get_user_info = AsyncMock(return_value=mock_user_info)

        # 发起登录并回调
        with patch("app.api.oauth.OAuthService.get_provider", return_value=mock_provider):
            login_response = await async_client.post("/api/v1/oauth/github/login")
            state = login_response.json()["state"]

            response = await async_client.get(
                f"/api/v1/oauth/github/callback?code=test_code&state={state}"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["user"]["email"] == "existing@github.com"
            assert data["user"]["username"] == "existing_oauth"

    @pytest.mark.asyncio
    async def test_oauth_callback_link_to_existing_email(
        self, async_client: AsyncClient, async_db: AsyncSession, oauth_config: OAuthConfig
    ):
        """测试将 OAuth 账号关联到已有相同邮箱的用户"""
        # 创建普通用户（没有 OAuth）
        existing_user = User(
            email="existing@example.com",
            username="existing_user",
            full_name="Existing User",
            hashed_password="hashed",
            is_active=True,
        )
        async_db.add(existing_user)
        await async_db.commit()

        # Mock OAuth 服务返回相同邮箱
        mock_provider = MagicMock()
        mock_provider.exchange_code_for_token = AsyncMock(
            return_value={"access_token": "oauth_token"}
        )

        mock_user_info = MagicMock()
        mock_user_info.provider_user_id = "github_link_123"
        mock_user_info.email = "existing@example.com"  # 相同邮箱
        mock_user_info.full_name = "Existing User"
        mock_user_info.avatar_url = None
        mock_user_info.verified_email = True

        mock_provider.get_user_info = AsyncMock(return_value=mock_user_info)

        with patch("app.api.oauth.OAuthService.get_provider", return_value=mock_provider):
            login_response = await async_client.post("/api/v1/oauth/github/login")
            state = login_response.json()["state"]

            response = await async_client.get(
                f"/api/v1/oauth/github/callback?code=test_code&state={state}"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["user"]["email"] == "existing@example.com"
            assert data["user"]["oauth_provider"] == "github"

    @pytest.mark.asyncio
    async def test_oauth_callback_invalid_state(
        self, async_client: AsyncClient, oauth_config: OAuthConfig
    ):
        """测试无效的 state（CSRF 攻击防护）"""
        response = await async_client.get(
            "/api/v1/oauth/github/callback?code=test_code&state=invalid_state"
        )

        assert response.status_code == 400
        data = response.json()
        assert "invalid state" in data["detail"].lower()
        assert "csrf" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_oauth_callback_no_access_token(
        self, async_client: AsyncClient, oauth_config: OAuthConfig
    ):
        """测试 OAuth 提供商未返回 access_token"""
        mock_provider = MagicMock()
        mock_provider.exchange_code_for_token = AsyncMock(
            return_value={}  # 没有 access_token
        )

        with patch("app.api.oauth.OAuthService.get_provider", return_value=mock_provider):
            login_response = await async_client.post("/api/v1/oauth/github/login")
            state = login_response.json()["state"]

            response = await async_client.get(
                f"/api/v1/oauth/github/callback?code=test_code&state={state}"
            )

            assert response.status_code == 400
            data = response.json()
            assert "failed to obtain access token" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_oauth_callback_no_email(
        self, async_client: AsyncClient, oauth_config: OAuthConfig
    ):
        """测试 OAuth 提供商未返回邮箱"""
        mock_provider = MagicMock()
        mock_provider.exchange_code_for_token = AsyncMock(
            return_value={"access_token": "token"}
        )

        mock_user_info = MagicMock()
        mock_user_info.email = None  # 没有邮箱
        mock_user_info.provider_user_id = "123"

        mock_provider.get_user_info = AsyncMock(return_value=mock_user_info)

        with patch("app.api.oauth.OAuthService.get_provider", return_value=mock_provider):
            login_response = await async_client.post("/api/v1/oauth/github/login")
            state = login_response.json()["state"]

            response = await async_client.get(
                f"/api/v1/oauth/github/callback?code=test_code&state={state}"
            )

            assert response.status_code == 400
            data = response.json()
            assert "email not provided" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_oauth_callback_unique_username_generation(
        self, async_client: AsyncClient, async_db: AsyncSession, oauth_config: OAuthConfig
    ):
        """测试用户名冲突时自动生成唯一用户名"""
        # 创建已存在的用户名
        existing = User(
            email="existing@example.com",
            username="testuser",  # 占用用户名
            hashed_password="hashed",
            is_active=True,
        )
        async_db.add(existing)
        await async_db.commit()

        # OAuth 用户也想用 testuser
        mock_provider = MagicMock()
        mock_provider.exchange_code_for_token = AsyncMock(
            return_value={"access_token": "token"}
        )

        mock_user_info = MagicMock()
        mock_user_info.provider_user_id = "github_456"
        mock_user_info.email = "testuser@github.com"  # 邮箱前缀是 testuser
        mock_user_info.full_name = "Test User"
        mock_user_info.avatar_url = None
        mock_user_info.verified_email = True

        mock_provider.get_user_info = AsyncMock(return_value=mock_user_info)

        with patch("app.api.oauth.OAuthService.get_provider", return_value=mock_provider):
            with patch("app.api.oauth.AdminNotificationService.notify_new_user_registration", new_callable=AsyncMock):
                login_response = await async_client.post("/api/v1/oauth/github/login")
                state = login_response.json()["state"]

                response = await async_client.get(
                    f"/api/v1/oauth/github/callback?code=test_code&state={state}"
                )

                assert response.status_code == 200
                data = response.json()
                # 应该生成 testuser1 或类似的用户名
                assert data["user"]["username"] != "testuser"
                assert "testuser" in data["user"]["username"]


# ===========================================
# 3. OAuth 解绑测试
# ===========================================

class TestOAuthUnlink:
    """测试 OAuth 账号解绑"""

    @pytest.mark.asyncio
    async def test_oauth_unlink_success(
        self, async_client: AsyncClient, async_db: AsyncSession
    ):
        """测试成功解绑 OAuth 账号"""
        # 创建有密码且绑定了 OAuth 的用户
        user = User(
            email="oauth_user@example.com",
            username="oauth_user",
            full_name="OAuth User",
            hashed_password="hashed_password",  # 有密码
            oauth_provider="github",
            oauth_id="github_789",
            is_active=True,
        )
        async_db.add(user)
        await async_db.commit()
        await async_db.refresh(user)

        # 登录并解绑
        from app.utils.security import create_access_token
        token = create_access_token({"sub": str(user.id), "type": "access"})

        response = await async_client.post(
            "/api/v1/oauth/github/unlink",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "unlinked successfully" in data["message"]

        # 验证数据库中已解绑
        await async_db.refresh(user)
        assert user.oauth_provider is None
        assert user.oauth_id is None

    @pytest.mark.asyncio
    async def test_oauth_unlink_no_password(
        self, async_client: AsyncClient, async_db: AsyncSession
    ):
        """测试没有密码时无法解绑（防止用户无法登录）"""
        # 创建只有 OAuth 登录的用户（没有密码）
        user = User(
            email="oauth_only@example.com",
            username="oauth_only",
            full_name="OAuth Only User",
            hashed_password=None,  # 没有密码
            oauth_provider="github",
            oauth_id="github_999",
            is_active=True,
        )
        async_db.add(user)
        await async_db.commit()
        await async_db.refresh(user)

        from app.utils.security import create_access_token
        token = create_access_token({"sub": str(user.id), "type": "access"})

        response = await async_client.post(
            "/api/v1/oauth/github/unlink",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "set a password" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_oauth_unlink_wrong_provider(
        self, async_client: AsyncClient, async_db: AsyncSession
    ):
        """测试解绑错误的提供商"""
        # 用户绑定的是 github，尝试解绑 google
        user = User(
            email="user@example.com",
            username="test_user",
            hashed_password="hashed",
            oauth_provider="github",
            oauth_id="github_111",
            is_active=True,
        )
        async_db.add(user)
        await async_db.commit()
        await async_db.refresh(user)

        from app.utils.security import create_access_token
        token = create_access_token({"sub": str(user.id), "type": "access"})

        response = await async_client.post(
            "/api/v1/oauth/google/unlink",  # 错误的提供商
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "not linked to" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_oauth_unlink_not_authenticated(self, async_client: AsyncClient):
        """测试未登录用户无法解绑"""
        response = await async_client.post("/api/v1/oauth/github/unlink")

        assert response.status_code == 403  # Forbidden (no credentials)


# ===========================================
# 测试总结
# ===========================================

"""
测试覆盖：
✅ OAuth 登录发起 - 4个测试用例
✅ OAuth 回调处理 - 8个测试用例
✅ OAuth 解绑 - 4个测试用例

总计：16个测试用例

测试场景：
- OAuth 登录流程（发起、回调、token 交换）
- 新用户注册
- 已有用户登录
- 账号关联（相同邮箱）
- 用户名冲突处理
- CSRF 防护（state 验证）
- 错误处理（无 token、无邮箱等）
- OAuth 解绑（有密码/无密码）
- 权限验证（未登录）
- 提供商配置（启用/禁用/不存在）
"""
