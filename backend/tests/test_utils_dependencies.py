"""
测试 Utils - Dependencies (依赖注入)
测试所有 FastAPI 依赖注入函数，包括用户认证、管理员认证等
"""
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, AdminUser
from app.utils.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    get_current_superadmin,
    get_current_user_optional,
)
from app.utils.security import create_access_token
from app.utils.token_blacklist import add_to_blacklist


# ===========================================
# 1. get_current_user 测试
# ===========================================

class TestGetCurrentUser:
    """测试获取当前用户"""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, async_db: AsyncSession, test_user: User):
        """测试成功获取当前用户"""
        # 创建有效的 access token
        token = create_access_token(
            data={"sub": str(test_user.id), "type": "access"}
        )
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        # 调用依赖函数
        user = await get_current_user(credentials=credentials, db=async_db)

        assert user.id == test_user.id
        assert user.email == test_user.email
        assert user.is_active

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, async_db: AsyncSession):
        """测试无效 token"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid_token"
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=async_db)

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_wrong_token_type(
        self, async_db: AsyncSession, test_user: User
    ):
        """测试错误的 token 类型（refresh 而非 access）"""
        # 创建 refresh token 而非 access token
        token = create_access_token(
            data={"sub": str(test_user.id), "type": "refresh"}
        )
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=async_db)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_blacklisted_token(
        self, async_db: AsyncSession, test_user: User
    ):
        """测试黑名单中的 token"""
        token = create_access_token(
            data={"sub": str(test_user.id), "type": "access"}
        )

        # 将 token 加入黑名单
        await add_to_blacklist(token)

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=async_db)

        assert exc_info.value.status_code == 401
        assert "revoked" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(self, async_db: AsyncSession):
        """测试用户不存在"""
        # 创建一个不存在的用户 ID
        token = create_access_token(data={"sub": "999999", "type": "access"})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=async_db)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_inactive_user(
        self, async_db: AsyncSession, test_user: User
    ):
        """测试未激活的用户"""
        # 将用户设为未激活
        test_user.is_active = False
        async_db.add(test_user)
        await async_db.commit()

        token = create_access_token(
            data={"sub": str(test_user.id), "type": "access"}
        )
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=async_db)

        assert exc_info.value.status_code == 401

        # 恢复用户状态
        test_user.is_active = True
        async_db.add(test_user)
        await async_db.commit()

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_user_id(self, async_db: AsyncSession):
        """测试无效的用户 ID 格式"""
        token = create_access_token(data={"sub": "invalid_id", "type": "access"})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=async_db)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_missing_sub(self, async_db: AsyncSession):
        """测试缺少 sub 字段"""
        token = create_access_token(data={"type": "access"})  # 没有 sub
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=async_db)

        assert exc_info.value.status_code == 401


# ===========================================
# 2. get_current_active_user 测试
# ===========================================

class TestGetCurrentActiveUser:
    """测试获取当前激活用户"""

    @pytest.mark.asyncio
    async def test_get_current_active_user_success(self, test_user: User):
        """测试成功获取激活用户"""
        test_user.is_active = True
        user = await get_current_active_user(current_user=test_user)
        assert user.id == test_user.id
        assert user.is_active

    @pytest.mark.asyncio
    async def test_get_current_active_user_inactive(self, test_user: User):
        """测试未激活用户"""
        test_user.is_active = False

        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(current_user=test_user)

        assert exc_info.value.status_code == 400
        assert "Inactive user" in exc_info.value.detail


# ===========================================
# 3. get_current_admin_user 测试
# ===========================================

class TestGetCurrentAdminUser:
    """测试获取当前管理员用户"""

    @pytest.mark.asyncio
    async def test_get_current_admin_user_success(
        self, async_db: AsyncSession, test_admin: AdminUser
    ):
        """测试成功获取管理员用户"""
        token = create_access_token(
            data={"sub": str(test_admin.id), "type": "access", "is_admin": True}
        )
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        admin = await get_current_admin_user(credentials=credentials, db=async_db)

        assert admin.id == test_admin.id
        assert admin.email == test_admin.email
        assert admin.is_active

    @pytest.mark.asyncio
    async def test_get_current_admin_user_not_admin_token(
        self, async_db: AsyncSession, test_user: User
    ):
        """测试使用普通用户 token（缺少 is_admin）"""
        token = create_access_token(
            data={"sub": str(test_user.id), "type": "access"}  # 没有 is_admin
        )
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_admin_user(credentials=credentials, db=async_db)

        assert exc_info.value.status_code == 401
        assert "admin" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_get_current_admin_user_blacklisted(
        self, async_db: AsyncSession, test_admin: AdminUser
    ):
        """测试黑名单中的管理员 token"""
        token = create_access_token(
            data={"sub": str(test_admin.id), "type": "access", "is_admin": True}
        )

        await add_to_blacklist(token)

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_admin_user(credentials=credentials, db=async_db)

        assert exc_info.value.status_code == 401
        assert "revoked" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_get_current_admin_user_not_found(self, async_db: AsyncSession):
        """测试管理员不存在"""
        token = create_access_token(
            data={"sub": "999999", "type": "access", "is_admin": True}
        )
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_admin_user(credentials=credentials, db=async_db)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_admin_user_inactive(
        self, async_db: AsyncSession, test_admin: AdminUser
    ):
        """测试未激活的管理员"""
        test_admin.is_active = False
        async_db.add(test_admin)
        await async_db.commit()

        token = create_access_token(
            data={"sub": str(test_admin.id), "type": "access", "is_admin": True}
        )
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_admin_user(credentials=credentials, db=async_db)

        assert exc_info.value.status_code == 401

        # 恢复状态
        test_admin.is_active = True
        async_db.add(test_admin)
        await async_db.commit()

    @pytest.mark.asyncio
    async def test_get_current_admin_user_invalid_token(self, async_db: AsyncSession):
        """测试无效 token"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid_token"
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_admin_user(credentials=credentials, db=async_db)

        assert exc_info.value.status_code == 401


# ===========================================
# 4. get_current_superadmin 测试
# ===========================================

class TestGetCurrentSuperadmin:
    """测试获取超级管理员"""

    @pytest.mark.asyncio
    async def test_get_current_superadmin_success(self, test_superadmin: AdminUser):
        """测试成功获取超级管理员"""
        admin = await get_current_superadmin(current_admin=test_superadmin)
        assert admin.id == test_superadmin.id
        assert admin.is_superadmin

    @pytest.mark.asyncio
    async def test_get_current_superadmin_not_superadmin(self, test_admin: AdminUser):
        """测试普通管理员（非超级管理员）"""
        test_admin.is_superadmin = False

        with pytest.raises(HTTPException) as exc_info:
            await get_current_superadmin(current_admin=test_admin)

        assert exc_info.value.status_code == 403
        assert "Superadmin" in exc_info.value.detail


# ===========================================
# 5. get_current_user_optional 测试
# ===========================================

class TestGetCurrentUserOptional:
    """测试获取可选用户（允许未认证）"""

    @pytest.mark.asyncio
    async def test_get_current_user_optional_with_valid_token(
        self, async_db: AsyncSession, test_user: User
    ):
        """测试有效 token"""
        token = create_access_token(
            data={"sub": str(test_user.id), "type": "access"}
        )
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        user = await get_current_user_optional(credentials=credentials, db=async_db)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    @pytest.mark.asyncio
    async def test_get_current_user_optional_no_credentials(
        self, async_db: AsyncSession
    ):
        """测试没有凭证（未登录）"""
        user = await get_current_user_optional(credentials=None, db=async_db)
        assert user is None

    @pytest.mark.asyncio
    async def test_get_current_user_optional_invalid_token(
        self, async_db: AsyncSession
    ):
        """测试无效 token（应返回 None 而非异常）"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid_token"
        )

        user = await get_current_user_optional(credentials=credentials, db=async_db)
        assert user is None

    @pytest.mark.asyncio
    async def test_get_current_user_optional_wrong_token_type(
        self, async_db: AsyncSession, test_user: User
    ):
        """测试错误的 token 类型（应返回 None）"""
        token = create_access_token(
            data={"sub": str(test_user.id), "type": "refresh"}
        )
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        user = await get_current_user_optional(credentials=credentials, db=async_db)
        assert user is None

    @pytest.mark.asyncio
    async def test_get_current_user_optional_user_not_found(
        self, async_db: AsyncSession
    ):
        """测试用户不存在（应返回 None）"""
        token = create_access_token(data={"sub": "999999", "type": "access"})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        user = await get_current_user_optional(credentials=credentials, db=async_db)
        assert user is None

    @pytest.mark.asyncio
    async def test_get_current_user_optional_inactive_user(
        self, async_db: AsyncSession, test_user: User
    ):
        """测试未激活用户（应返回 None）"""
        test_user.is_active = False
        async_db.add(test_user)
        await async_db.commit()

        token = create_access_token(
            data={"sub": str(test_user.id), "type": "access"}
        )
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        user = await get_current_user_optional(credentials=credentials, db=async_db)
        assert user is None

        # 恢复状态
        test_user.is_active = True
        async_db.add(test_user)
        await async_db.commit()

    @pytest.mark.asyncio
    async def test_get_current_user_optional_invalid_user_id(
        self, async_db: AsyncSession
    ):
        """测试无效用户 ID（应返回 None）"""
        token = create_access_token(data={"sub": "invalid_id", "type": "access"})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        user = await get_current_user_optional(credentials=credentials, db=async_db)
        assert user is None

    @pytest.mark.asyncio
    async def test_get_current_user_optional_missing_sub(
        self, async_db: AsyncSession
    ):
        """测试缺少 sub 字段（应返回 None）"""
        token = create_access_token(data={"type": "access"})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        user = await get_current_user_optional(credentials=credentials, db=async_db)
        assert user is None


# ===========================================
# 测试总结
# ===========================================

"""
测试覆盖：
✅ get_current_user - 8个测试用例
✅ get_current_active_user - 2个测试用例
✅ get_current_admin_user - 6个测试用例
✅ get_current_superadmin - 2个测试用例
✅ get_current_user_optional - 8个测试用例

总计：26个测试用例

测试场景：
- 成功获取用户/管理员
- 无效 token
- 错误的 token 类型
- 黑名单 token
- 用户/管理员不存在
- 未激活用户
- 无效 ID 格式
- 缺少必要字段
- 权限验证（超级管理员）
- 可选认证（允许未登录）
"""
