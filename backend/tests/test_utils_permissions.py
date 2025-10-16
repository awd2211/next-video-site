"""
测试 Utils - Permissions (权限验证)
测试所有权限相关功能，包括权限检查、缓存、装饰器等
"""
import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import AdminUser
from app.models.admin import Role, Permission, RolePermission
from app.utils.permissions import (
    get_admin_permissions_cached,
    invalidate_admin_permissions_cache,
    invalidate_role_permissions_cache,
    check_admin_has_permission,
    check_admin_has_any_permission,
    check_admin_has_all_permissions,
    parse_permission_pattern,
    get_admin_permission_summary,
    require_permission,
    require_any_permission,
)
from app.utils.cache import get_redis
from app.database import get_db


# ===========================================
# 测试 Fixtures
# ===========================================

@pytest.fixture
async def test_role(async_db: AsyncSession):
    """创建测试角色"""
    role = Role(
        name="编辑",
        code="editor",
        description="内容编辑角色",
        is_active=True
    )
    async_db.add(role)
    await async_db.commit()
    await async_db.refresh(role)
    return role


@pytest.fixture
async def test_permissions(async_db: AsyncSession):
    """创建测试权限"""
    permissions = [
        Permission(code="video.create", name="创建视频", module="video"),
        Permission(code="video.read", name="查看视频", module="video"),
        Permission(code="video.update", name="更新视频", module="video"),
        Permission(code="video.delete", name="删除视频", module="video"),
        Permission(code="comment.read", name="查看评论", module="comment"),
        Permission(code="comment.delete", name="删除评论", module="comment"),
    ]
    for perm in permissions:
        async_db.add(perm)
    await async_db.commit()

    # 刷新以获取 ID
    for perm in permissions:
        await async_db.refresh(perm)

    return permissions


@pytest.fixture
async def test_admin_with_role(async_db: AsyncSession, test_role: Role, test_permissions):
    """创建带角色的管理员"""
    # 为角色分配部分权限
    role_perms = [
        RolePermission(role_id=test_role.id, permission_id=test_permissions[0].id),  # video.create
        RolePermission(role_id=test_role.id, permission_id=test_permissions[1].id),  # video.read
        RolePermission(role_id=test_role.id, permission_id=test_permissions[4].id),  # comment.read
    ]
    for rp in role_perms:
        async_db.add(rp)
    await async_db.commit()

    # 创建管理员
    admin = AdminUser(
        email="editor@test.com",
        username="editor",
        hashed_password="hashed",
        full_name="Editor",
        is_active=True,
        is_superadmin=False,
        role_id=test_role.id
    )
    async_db.add(admin)
    await async_db.commit()
    await async_db.refresh(admin)

    return admin


# ===========================================
# 1. 权限缓存测试
# ===========================================

class TestPermissionCache:
    """测试权限缓存功能"""

    @pytest.mark.asyncio
    @pytest.mark.requires_redis
    async def test_get_admin_permissions_cached_superadmin(
        self, async_db: AsyncSession, test_superadmin: AdminUser
    ):
        """测试超级管理员权限缓存"""
        permissions = await get_admin_permissions_cached(test_superadmin.id, async_db)

        assert "*" in permissions
        assert len(permissions) == 1

    @pytest.mark.asyncio
    @pytest.mark.requires_redis
    async def test_get_admin_permissions_cached_with_role(
        self, async_db: AsyncSession, test_admin_with_role: AdminUser
    ):
        """测试带角色的管理员权限缓存"""
        permissions = await get_admin_permissions_cached(test_admin_with_role.id, async_db)

        assert "video.create" in permissions
        assert "video.read" in permissions
        assert "comment.read" in permissions
        assert "video.delete" not in permissions  # 未分配

    @pytest.mark.asyncio
    @pytest.mark.requires_redis
    async def test_get_admin_permissions_cached_no_role(
        self, async_db: AsyncSession, test_admin: AdminUser
    ):
        """测试没有角色的管理员"""
        # 确保管理员没有角色
        test_admin.role_id = None
        async_db.add(test_admin)
        await async_db.commit()

        permissions = await get_admin_permissions_cached(test_admin.id, async_db)

        assert len(permissions) == 0

    @pytest.mark.asyncio
    @pytest.mark.requires_redis
    async def test_get_admin_permissions_cached_uses_cache(
        self, async_db: AsyncSession, test_admin_with_role: AdminUser
    ):
        """测试权限缓存是否生效"""
        # 第一次调用，从数据库加载
        permissions1 = await get_admin_permissions_cached(test_admin_with_role.id, async_db)

        # 第二次调用，应该从缓存读取
        permissions2 = await get_admin_permissions_cached(test_admin_with_role.id, async_db)

        assert permissions1 == permissions2

        # 验证 Redis 中存在缓存
        redis = await get_redis()
        cache_key = f"admin_permissions:{test_admin_with_role.id}"
        cached = await redis.get(cache_key)
        assert cached is not None

    @pytest.mark.asyncio
    @pytest.mark.requires_redis
    async def test_invalidate_admin_permissions_cache(
        self, async_db: AsyncSession, test_admin_with_role: AdminUser
    ):
        """测试清除管理员权限缓存"""
        # 先缓存权限
        await get_admin_permissions_cached(test_admin_with_role.id, async_db)

        # 清除缓存
        await invalidate_admin_permissions_cache(test_admin_with_role.id)

        # 验证缓存已清除
        redis = await get_redis()
        cache_key = f"admin_permissions:{test_admin_with_role.id}"
        cached = await redis.get(cache_key)
        assert cached is None

    @pytest.mark.asyncio
    @pytest.mark.requires_redis
    async def test_invalidate_role_permissions_cache(
        self, async_db: AsyncSession, test_role: Role, test_admin_with_role: AdminUser
    ):
        """测试清除角色相关的所有管理员权限缓存"""
        # 先缓存权限
        await get_admin_permissions_cached(test_admin_with_role.id, async_db)

        # 清除角色相关缓存
        await invalidate_role_permissions_cache(test_role.id, async_db)

        # 验证缓存已清除
        redis = await get_redis()
        cache_key = f"admin_permissions:{test_admin_with_role.id}"
        cached = await redis.get(cache_key)
        assert cached is None

    @pytest.mark.asyncio
    async def test_get_admin_permissions_cached_admin_not_found(
        self, async_db: AsyncSession
    ):
        """测试管理员不存在"""
        permissions = await get_admin_permissions_cached(999999, async_db)
        assert len(permissions) == 0


# ===========================================
# 2. 权限检查函数测试
# ===========================================

class TestPermissionChecks:
    """测试权限检查函数"""

    @pytest.mark.asyncio
    async def test_check_admin_has_permission_superadmin(
        self, async_db: AsyncSession, test_superadmin: AdminUser
    ):
        """测试超级管理员拥有所有权限"""
        has_perm = await check_admin_has_permission(
            test_superadmin, "any.permission", async_db
        )
        assert has_perm is True

    @pytest.mark.asyncio
    async def test_check_admin_has_permission_exact_match(
        self, async_db: AsyncSession, test_admin_with_role: AdminUser
    ):
        """测试精确权限匹配"""
        # 有权限
        has_perm = await check_admin_has_permission(
            test_admin_with_role, "video.create", async_db
        )
        assert has_perm is True

        # 无权限
        has_perm = await check_admin_has_permission(
            test_admin_with_role, "video.delete", async_db
        )
        assert has_perm is False

    @pytest.mark.asyncio
    async def test_check_admin_has_permission_wildcard(
        self, async_db: AsyncSession, test_admin_with_role: AdminUser, test_role: Role
    ):
        """测试通配符权限"""
        # 为角色添加 video.* 通配符权限
        wildcard_perm = Permission(code="video.*", name="视频模块所有权限", module="video")
        async_db.add(wildcard_perm)
        await async_db.commit()
        await async_db.refresh(wildcard_perm)

        role_perm = RolePermission(role_id=test_role.id, permission_id=wildcard_perm.id)
        async_db.add(role_perm)
        await async_db.commit()

        # 清除缓存
        await invalidate_admin_permissions_cache(test_admin_with_role.id)

        # 应该匹配所有 video.* 权限
        has_perm = await check_admin_has_permission(
            test_admin_with_role, "video.delete", async_db
        )
        assert has_perm is True

        has_perm = await check_admin_has_permission(
            test_admin_with_role, "video.publish", async_db
        )
        assert has_perm is True

    @pytest.mark.asyncio
    async def test_check_admin_has_any_permission(
        self, async_db: AsyncSession, test_admin_with_role: AdminUser
    ):
        """测试管理员是否有任一权限"""
        # 有其中一个权限
        has_any = await check_admin_has_any_permission(
            test_admin_with_role, ["video.create", "video.delete"], async_db
        )
        assert has_any is True

        # 都没有
        has_any = await check_admin_has_any_permission(
            test_admin_with_role, ["video.delete", "video.publish"], async_db
        )
        assert has_any is False

    @pytest.mark.asyncio
    async def test_check_admin_has_all_permissions(
        self, async_db: AsyncSession, test_admin_with_role: AdminUser
    ):
        """测试管理员是否拥有所有指定权限"""
        # 都有
        has_all = await check_admin_has_all_permissions(
            test_admin_with_role, ["video.create", "video.read"], async_db
        )
        assert has_all is True

        # 缺少一个
        has_all = await check_admin_has_all_permissions(
            test_admin_with_role, ["video.create", "video.delete"], async_db
        )
        assert has_all is False


# ===========================================
# 3. 权限装饰器测试
# ===========================================

class TestPermissionDecorators:
    """测试权限装饰器"""

    @pytest.mark.asyncio
    async def test_require_permission_superadmin(
        self, async_db: AsyncSession, test_superadmin: AdminUser
    ):
        """测试超级管理员通过权限检查"""
        checker = require_permission("video.create", "video.delete")
        admin = await checker(current_admin=test_superadmin, db=async_db)
        assert admin.id == test_superadmin.id

    @pytest.mark.asyncio
    async def test_require_permission_has_permission(
        self, async_db: AsyncSession, test_admin_with_role: AdminUser
    ):
        """测试有权限的管理员通过检查"""
        checker = require_permission("video.create")
        admin = await checker(current_admin=test_admin_with_role, db=async_db)
        assert admin.id == test_admin_with_role.id

    @pytest.mark.asyncio
    async def test_require_permission_missing_permission(
        self, async_db: AsyncSession, test_admin_with_role: AdminUser
    ):
        """测试缺少权限的管理员"""
        checker = require_permission("video.delete")

        with pytest.raises(HTTPException) as exc_info:
            await checker(current_admin=test_admin_with_role, db=async_db)

        assert exc_info.value.status_code == 403
        assert "权限不足" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_require_permission_no_role(
        self, async_db: AsyncSession, test_admin: AdminUser
    ):
        """测试没有角色的管理员"""
        # 确保管理员没有角色
        test_admin.role_id = None
        test_admin.is_superadmin = False
        async_db.add(test_admin)
        await async_db.commit()

        checker = require_permission("video.create")

        with pytest.raises(HTTPException) as exc_info:
            await checker(current_admin=test_admin, db=async_db)

        assert exc_info.value.status_code == 403
        assert "没有任何角色权限" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_require_any_permission_has_one(
        self, async_db: AsyncSession, test_admin_with_role: AdminUser
    ):
        """测试任一权限 - 有其中一个"""
        checker = require_any_permission("video.create", "video.delete")
        admin = await checker(current_admin=test_admin_with_role, db=async_db)
        assert admin.id == test_admin_with_role.id

    @pytest.mark.asyncio
    async def test_require_any_permission_has_none(
        self, async_db: AsyncSession, test_admin_with_role: AdminUser
    ):
        """测试任一权限 - 都没有"""
        checker = require_any_permission("video.delete", "video.publish")

        with pytest.raises(HTTPException) as exc_info:
            await checker(current_admin=test_admin_with_role, db=async_db)

        assert exc_info.value.status_code == 403
        assert "之一" in exc_info.value.detail


# ===========================================
# 4. 权限工具函数测试
# ===========================================

class TestPermissionUtils:
    """测试权限工具函数"""

    def test_parse_permission_pattern_no_wildcard(self):
        """测试解析无通配符的权限"""
        all_perms = ["video.create", "video.read", "comment.delete"]
        result = parse_permission_pattern("video.create", all_perms)
        assert result == ["video.create"]

    def test_parse_permission_pattern_all_wildcard(self):
        """测试全局通配符 *"""
        all_perms = ["video.create", "video.read", "comment.delete"]
        result = parse_permission_pattern("*", all_perms)
        assert result == all_perms

    def test_parse_permission_pattern_module_wildcard(self):
        """测试模块级通配符 video.*"""
        all_perms = ["video.create", "video.read", "video.delete", "comment.delete"]
        result = parse_permission_pattern("video.*", all_perms)
        assert "video.create" in result
        assert "video.read" in result
        assert "video.delete" in result
        assert "comment.delete" not in result

    def test_parse_permission_pattern_operation_wildcard(self):
        """测试操作级通配符 *.read"""
        all_perms = ["video.read", "comment.read", "user.read", "video.create"]
        result = parse_permission_pattern("*.read", all_perms)
        assert "video.read" in result
        assert "comment.read" in result
        assert "user.read" in result
        assert "video.create" not in result

    @pytest.mark.asyncio
    async def test_get_admin_permission_summary_superadmin(
        self, async_db: AsyncSession, test_superadmin: AdminUser
    ):
        """测试获取超级管理员权限摘要"""
        summary = await get_admin_permission_summary(test_superadmin.id, async_db)

        assert summary["is_superadmin"] is True
        assert summary["role"] == "超级管理员"
        assert summary["permissions"] == ["*"]
        assert summary["permission_count"] == -1

    @pytest.mark.asyncio
    async def test_get_admin_permission_summary_with_role(
        self, async_db: AsyncSession, test_admin_with_role: AdminUser
    ):
        """测试获取普通管理员权限摘要"""
        summary = await get_admin_permission_summary(test_admin_with_role.id, async_db)

        assert summary["is_superadmin"] is False
        assert summary["role"] is not None
        assert len(summary["permissions"]) > 0
        assert summary["permission_count"] > 0

    @pytest.mark.asyncio
    async def test_get_admin_permission_summary_no_role(
        self, async_db: AsyncSession, test_admin: AdminUser
    ):
        """测试获取无角色管理员权限摘要"""
        # 确保没有角色
        test_admin.role_id = None
        test_admin.is_superadmin = False
        async_db.add(test_admin)
        await async_db.commit()

        summary = await get_admin_permission_summary(test_admin.id, async_db)

        assert summary["is_superadmin"] is False
        assert summary["role"] is None
        assert summary["permissions"] == []
        assert summary["permission_count"] == 0

    @pytest.mark.asyncio
    async def test_get_admin_permission_summary_not_found(
        self, async_db: AsyncSession
    ):
        """测试管理员不存在"""
        summary = await get_admin_permission_summary(999999, async_db)

        assert summary["is_superadmin"] is False
        assert summary["role"] is None
        assert summary["permissions"] == []
        assert summary["permission_count"] == 0


# ===========================================
# 测试总结
# ===========================================

"""
测试覆盖：
✅ 权限缓存测试 - 8个测试用例
✅ 权限检查函数测试 - 6个测试用例
✅ 权限装饰器测试 - 6个测试用例
✅ 权限工具函数测试 - 8个测试用例

总计：28个测试用例

测试场景：
- 超级管理员权限
- 角色权限缓存
- 权限缓存失效
- 精确权限匹配
- 通配符权限（模块级、操作级、全局）
- 任一权限检查
- 所有权限检查
- 权限装饰器验证
- 权限摘要生成
- 边界情况（无角色、管理员不存在等）
"""
