"""
权限验证工具模块
提供便捷的权限检查装饰器和工具函数
"""

from typing import List, Set, Optional, Callable
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from functools import wraps

from app.database import get_db
from app.models.user import AdminUser
from app.models.admin import Role, RolePermission
from app.utils.dependencies import get_current_admin_user
from app.utils.cache import get_redis
import json


# ========== 权限缓存 ==========


async def get_admin_permissions_cached(admin_id: int, db: AsyncSession) -> Set[str]:
    """
    获取管理员权限(带Redis缓存)
    缓存时间: 30分钟
    """
    try:
        redis = await get_redis()
        cache_key = f"admin_permissions:{admin_id}"

        # 尝试从缓存获取
        cached = await redis.get(cache_key)
        if cached:
            return set(json.loads(cached))
    except Exception:
        # Redis不可用时直接查询数据库
        pass

    # 从数据库加载权限
    result = await db.execute(
        select(AdminUser)
        .where(AdminUser.id == admin_id)
        .options(
            selectinload(AdminUser.role)
            .selectinload(Role.role_permissions)
            .selectinload(RolePermission.permission)
        )
    )
    admin = result.scalar_one_or_none()

    if not admin:
        return set()

    # 超级管理员拥有所有权限
    if admin.is_superadmin:
        permissions = {"*"}
    elif admin.role:
        permissions = {p.code for p in admin.role.permissions}
    else:
        permissions = set()

    # 缓存30分钟
    try:
        redis = await get_redis()
        await redis.setex(cache_key, 1800, json.dumps(list(permissions)))
    except Exception:
        pass

    return permissions


async def invalidate_admin_permissions_cache(admin_id: int):
    """清除管理员权限缓存"""
    try:
        redis = await get_redis()
        await redis.delete(f"admin_permissions:{admin_id}")
    except Exception:
        pass


async def invalidate_role_permissions_cache(role_id: int, db: AsyncSession):
    """清除角色相关的所有管理员权限缓存"""
    try:
        # 查找所有使用该角色的管理员
        result = await db.execute(
            select(AdminUser.id).where(AdminUser.role_id == role_id)
        )
        admin_ids = [row[0] for row in result.all()]

        # 批量清除缓存
        if admin_ids:
            redis = await get_redis()
            cache_keys = [f"admin_permissions:{aid}" for aid in admin_ids]
            await redis.delete(*cache_keys)
    except Exception:
        pass


# ========== 权限检查函数 ==========


async def check_admin_has_permission(
    admin: AdminUser,
    permission_code: str,
    db: AsyncSession
) -> bool:
    """
    检查管理员是否有指定权限

    Args:
        admin: 管理员对象
        permission_code: 权限代码(如 "video.create")
        db: 数据库会话

    Returns:
        bool: 是否有权限
    """
    # 超级管理员拥有所有权限
    if admin.is_superadmin:
        return True

    # 获取管理员权限(带缓存)
    permissions = await get_admin_permissions_cached(admin.id, db)

    # 通配符权限
    if "*" in permissions:
        return True

    # 精确匹配
    if permission_code in permissions:
        return True

    # 模块级通配符 (如 video.* 匹配 video.create)
    module = permission_code.split(".")[0]
    if f"{module}.*" in permissions:
        return True

    return False


async def check_admin_has_any_permission(
    admin: AdminUser,
    permission_codes: List[str],
    db: AsyncSession
) -> bool:
    """检查管理员是否有任一权限"""
    for code in permission_codes:
        if await check_admin_has_permission(admin, code, db):
            return True
    return False


async def check_admin_has_all_permissions(
    admin: AdminUser,
    permission_codes: List[str],
    db: AsyncSession
) -> bool:
    """检查管理员是否拥有所有指定权限"""
    for code in permission_codes:
        if not await check_admin_has_permission(admin, code, db):
            return False
    return True


# ========== 权限装饰器依赖项 ==========


def require_permission(*permission_codes: str):
    """
    权限验证依赖项装饰器

    用法:
        @router.post("/videos", dependencies=[Depends(require_permission("video.create"))])
        async def create_video(...):
            pass

    Args:
        *permission_codes: 所需的权限代码列表

    Returns:
        依赖项函数
    """
    async def permission_checker(
        current_admin: AdminUser = Depends(get_current_admin_user),
        db: AsyncSession = Depends(get_db)
    ) -> AdminUser:
        # 超级管理员跳过检查
        if current_admin.is_superadmin:
            return current_admin

        # 获取管理员权限
        permissions = await get_admin_permissions_cached(current_admin.id, db)

        # 检查是否有角色
        if not permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您没有任何角色权限，无法执行此操作"
            )

        # 检查所需权限
        required_permissions = set(permission_codes)

        # 通配符权限
        if "*" in permissions:
            return current_admin

        # 检查每个所需权限
        missing_permissions = []
        for required in required_permissions:
            # 精确匹配
            if required in permissions:
                continue

            # 模块级通配符
            module = required.split(".")[0]
            if f"{module}.*" in permissions:
                continue

            missing_permissions.append(required)

        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足。需要以下权限: {', '.join(missing_permissions)}"
            )

        return current_admin

    return permission_checker


def require_any_permission(*permission_codes: str):
    """
    要求拥有任一权限

    用法:
        @router.get("/videos", dependencies=[Depends(require_any_permission("video.read", "video.review"))])
    """
    async def permission_checker(
        current_admin: AdminUser = Depends(get_current_admin_user),
        db: AsyncSession = Depends(get_db)
    ) -> AdminUser:
        if current_admin.is_superadmin:
            return current_admin

        permissions = await get_admin_permissions_cached(current_admin.id, db)

        if not permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您没有任何角色权限"
            )

        # 通配符
        if "*" in permissions:
            return current_admin

        # 检查是否有任一权限
        for required in permission_codes:
            if required in permissions:
                return current_admin

            module = required.split(".")[0]
            if f"{module}.*" in permissions:
                return current_admin

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足。需要以下权限之一: {', '.join(permission_codes)}"
        )

    return permission_checker


# ========== 资源所有权检查 ==========


async def check_resource_ownership(
    resource_type: str,
    resource_id: int,
    current_admin: AdminUser,
    db: AsyncSession
) -> bool:
    """
    检查管理员是否拥有资源

    Args:
        resource_type: 资源类型 (video, comment, banner, announcement, etc.)
        resource_id: 资源ID
        current_admin: 当前管理员
        db: 数据库会话

    Returns:
        bool: 是否拥有资源
    """
    # 超级管理员拥有所有资源
    if current_admin.is_superadmin:
        return True

    # ✅ 根据资源类型查询所有权
    try:
        if resource_type == "video":
            from app.models.video import Video
            result = await db.execute(
                select(Video).where(
                    Video.id == resource_id,
                    Video.uploaded_by_admin_id == current_admin.id
                )
            )
            return result.scalar_one_or_none() is not None

        elif resource_type == "comment":
            from app.models.comment import Comment
            # 评论没有 admin_id，检查是否可以管理
            result = await db.execute(
                select(Comment).where(Comment.id == resource_id)
            )
            return result.scalar_one_or_none() is not None

        elif resource_type == "banner":
            from app.models.banner import Banner
            result = await db.execute(
                select(Banner).where(
                    Banner.id == resource_id,
                    Banner.created_by_admin_id == current_admin.id
                )
            )
            return result.scalar_one_or_none() is not None

        elif resource_type == "announcement":
            from app.models.announcement import Announcement
            result = await db.execute(
                select(Announcement).where(
                    Announcement.id == resource_id,
                    Announcement.created_by_admin_id == current_admin.id
                )
            )
            return result.scalar_one_or_none() is not None

        elif resource_type == "media":
            from app.models.media import Media
            result = await db.execute(
                select(Media).where(
                    Media.id == resource_id,
                    Media.uploaded_by_admin_id == current_admin.id
                )
            )
            return result.scalar_one_or_none() is not None

        elif resource_type == "schedule":
            from app.models.scheduling import ContentSchedule
            result = await db.execute(
                select(ContentSchedule).where(
                    ContentSchedule.id == resource_id,
                    ContentSchedule.created_by == current_admin.id
                )
            )
            return result.scalar_one_or_none() is not None

        else:
            # 未知资源类型，拒绝访问
            return False

    except Exception as e:
        # 查询出错，拒绝访问
        return False


# ========== 权限工具函数 ==========


def parse_permission_pattern(pattern: str, all_permissions: List[str]) -> List[str]:
    """
    解析权限模式(支持通配符)

    Args:
        pattern: 权限模式 (如 "video.*", "*.read")
        all_permissions: 所有可用权限列表

    Returns:
        匹配的权限列表
    """
    if "*" not in pattern:
        return [pattern]

    matched = []

    if pattern == "*":
        # 所有权限
        return all_permissions
    elif pattern.endswith(".*"):
        # 模块级通配符 (video.*)
        module = pattern[:-2]
        matched = [p for p in all_permissions if p.startswith(f"{module}.")]
    elif pattern.startswith("*."):
        # 操作级通配符 (*.read)
        operation = pattern[2:]
        matched = [p for p in all_permissions if p.endswith(f".{operation}")]

    return matched


async def get_admin_permission_summary(admin_id: int, db: AsyncSession) -> dict:
    """
    获取管理员权限摘要

    Returns:
        {
            "is_superadmin": bool,
            "role": str,
            "permissions": List[str],
            "permission_count": int
        }
    """
    result = await db.execute(
        select(AdminUser)
        .where(AdminUser.id == admin_id)
        .options(
            selectinload(AdminUser.role)
            .selectinload(Role.role_permissions)
            .selectinload(RolePermission.permission)
        )
    )
    admin = result.scalar_one_or_none()

    if not admin:
        return {
            "is_superadmin": False,
            "role": None,
            "permissions": [],
            "permission_count": 0
        }

    if admin.is_superadmin:
        return {
            "is_superadmin": True,
            "role": "超级管理员",
            "permissions": ["*"],
            "permission_count": -1  # 表示所有权限
        }

    permissions = []
    if admin.role:
        permissions = [p.code for p in admin.role.permissions]

    return {
        "is_superadmin": False,
        "role": admin.role.name if admin.role else None,
        "permissions": permissions,
        "permission_count": len(permissions)
    }
