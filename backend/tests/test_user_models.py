"""
测试用户相关模型
包括: User, AdminUser, Role, Permission
"""
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.user import User, AdminUser
from app.models.admin import Role, Permission
from app.database import AsyncSessionLocal
from app.utils.security import get_password_hash


@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestUserModel:
    """User 模型测试"""

    async def test_create_user(self):
        """测试创建用户"""
        async with AsyncSessionLocal() as db:
            user = User(
                email="test_model@example.com",
                username="test_model_user",
                hashed_password=get_password_hash("password123"),
                full_name="Test Model User",
                is_active=True
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            assert user.id is not None
            assert user.email == "test_model@example.com"
            assert user.username == "test_model_user"
            assert user.is_active is True
            
            # 清理
            await db.delete(user)
            await db.commit()

    async def test_user_unique_email(self):
        """测试邮箱唯一性约束"""
        async with AsyncSessionLocal() as db:
            # 创建第一个用户
            user1 = User(
                email="unique_email@example.com",
                username="user1",
                hashed_password=get_password_hash("password")
            )
            db.add(user1)
            await db.commit()
            
            # 尝试创建相同邮箱的用户
            user2 = User(
                email="unique_email@example.com",
                username="user2",
                hashed_password=get_password_hash("password")
            )
            db.add(user2)
            
            with pytest.raises(IntegrityError):
                await db.commit()
            
            await db.rollback()
            await db.delete(user1)
            await db.commit()

    async def test_user_unique_username(self):
        """测试用户名唯一性约束"""
        async with AsyncSessionLocal() as db:
            user1 = User(
                email="user1@example.com",
                username="unique_username",
                hashed_password=get_password_hash("password")
            )
            db.add(user1)
            await db.commit()
            
            user2 = User(
                email="user2@example.com",
                username="unique_username",
                hashed_password=get_password_hash("password")
            )
            db.add(user2)
            
            with pytest.raises(IntegrityError):
                await db.commit()
            
            await db.rollback()
            await db.delete(user1)
            await db.commit()

    async def test_user_default_values(self):
        """测试用户默认值"""
        async with AsyncSessionLocal() as db:
            user = User(
                email="defaults@example.com",
                username="defaults_user",
                hashed_password=get_password_hash("password")
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            assert user.is_active is True  # 默认激活
            assert user.is_verified is False  # 默认未验证
            assert user.is_vip is False  # 默认非VIP
            assert user.created_at is not None
            
            await db.delete(user)
            await db.commit()

    async def test_user_password_hashing(self):
        """测试密码不存储明文"""
        async with AsyncSessionLocal() as db:
            plain_password = "my_secret_password"
            user = User(
                email="password_test@example.com",
                username="password_user",
                hashed_password=get_password_hash(plain_password)
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            # 密码应该被哈希
            assert user.hashed_password != plain_password
            assert len(user.hashed_password) > 0
            
            await db.delete(user)
            await db.commit()


@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestAdminUserModel:
    """AdminUser 模型测试"""

    async def test_create_admin_user(self):
        """测试创建管理员用户"""
        async with AsyncSessionLocal() as db:
            admin = AdminUser(
                email="admin_test@example.com",
                username="admin_test",
                hashed_password=get_password_hash("admin_password"),
                full_name="Test Admin",
                is_active=True,
                is_superadmin=False
            )
            db.add(admin)
            await db.commit()
            await db.refresh(admin)
            
            assert admin.id is not None
            assert admin.username == "admin_test"
            assert admin.is_superadmin is False
            
            await db.delete(admin)
            await db.commit()

    async def test_admin_unique_username(self):
        """测试管理员用户名唯一性"""
        async with AsyncSessionLocal() as db:
            admin1 = AdminUser(
                email="admin1@example.com",
                username="unique_admin",
                hashed_password=get_password_hash("password")
            )
            db.add(admin1)
            await db.commit()
            
            admin2 = AdminUser(
                email="admin2@example.com",
                username="unique_admin",
                hashed_password=get_password_hash("password")
            )
            db.add(admin2)
            
            with pytest.raises(IntegrityError):
                await db.commit()
            
            await db.rollback()
            await db.delete(admin1)
            await db.commit()

    async def test_superadmin_flag(self):
        """测试超级管理员标志"""
        async with AsyncSessionLocal() as db:
            superadmin = AdminUser(
                email="super@example.com",
                username="superadmin_test",
                hashed_password=get_password_hash("password"),
                is_superadmin=True
            )
            db.add(superadmin)
            await db.commit()
            await db.refresh(superadmin)
            
            assert superadmin.is_superadmin is True
            
            await db.delete(superadmin)
            await db.commit()


@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestRoleModel:
    """Role 模型测试"""

    async def test_create_role(self):
        """测试创建角色"""
        async with AsyncSessionLocal() as db:
            role = Role(
                name="Test Role",
                description="Test role description"
            )
            db.add(role)
            await db.commit()
            await db.refresh(role)
            
            assert role.id is not None
            assert role.name == "Test Role"
            
            await db.delete(role)
            await db.commit()

    async def test_role_unique_name(self):
        """测试角色名称唯一性"""
        async with AsyncSessionLocal() as db:
            role1 = Role(name="Unique Role")
            db.add(role1)
            await db.commit()
            
            role2 = Role(name="Unique Role")
            db.add(role2)
            
            with pytest.raises(IntegrityError):
                await db.commit()
            
            await db.rollback()
            await db.delete(role1)
            await db.commit()


@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestPermissionModel:
    """Permission 模型测试"""

    async def test_create_permission(self):
        """测试创建权限"""
        async with AsyncSessionLocal() as db:
            permission = Permission(
                name="test.read",
                description="Test read permission"
            )
            db.add(permission)
            await db.commit()
            await db.refresh(permission)
            
            assert permission.id is not None
            assert permission.name == "test.read"
            
            await db.delete(permission)
            await db.commit()

