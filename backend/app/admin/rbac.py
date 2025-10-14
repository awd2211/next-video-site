"""
角色权限管理 API (RBAC - Role-Based Access Control)
支持角色创建、权限分配、管理员角色管理
"""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.admin import Permission, Role, RolePermission
from app.models.user import AdminUser
from app.utils.dependencies import get_current_admin_user, get_current_superadmin

router = APIRouter()


# ========== Pydantic Schemas ==========


class PermissionBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    module: str  # videos, users, comments, settings, etc.


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permission_ids: List[int] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None


class RoleResponse(RoleBase):
    id: int
    is_active: bool
    created_at: datetime
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True


class AdminUserRoleAssignment(BaseModel):
    role_id: Optional[int] = None  # None to unassign role


class AdminUserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_superadmin: bool
    created_at: datetime
    last_login: Optional[datetime]
    role: Optional[RoleResponse] = None

    class Config:
        from_attributes = True


# ========== Permission Endpoints ==========


@router.get("/permissions", response_model=dict)
async def list_permissions(
    module: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """
    获取所有权限列表
    可选按模块类型筛选
    """
    query = select(Permission).order_by(Permission.module, Permission.code)

    if module:
        query = query.where(Permission.module == module)

    result = await db.execute(query)
    permissions = result.scalars().all()

    # 按模块分组
    grouped = {}
    for perm in permissions:
        if perm.module not in grouped:
            grouped[perm.module] = []
        grouped[perm.module].append(
            {
                "id": perm.id,
                "name": perm.name,
                "code": perm.code,
                "module": perm.module,
                "description": perm.description,
            }
        )

    return {"permissions": permissions, "grouped": grouped, "total": len(permissions)}


@router.post("/permissions", response_model=PermissionResponse)
async def create_permission(
    permission: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """创建新权限"""
    # 检查code是否重复
    existing = await db.execute(select(Permission).where(Permission.code == permission.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="权限代码已存在")

    new_permission = Permission(**permission.dict())
    db.add(new_permission)
    await db.commit()
    await db.refresh(new_permission)

    logger.info(f"管理员 {current_admin.username} 创建了权限: {permission.code}")
    return new_permission


@router.delete("/permissions/{permission_id}")
async def delete_permission(
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """删除权限"""
    result = await db.execute(select(Permission).where(Permission.id == permission_id))
    permission = result.scalar_one_or_none()

    if not permission:
        raise HTTPException(status_code=404, detail="权限不存在")

    await db.delete(permission)
    await db.commit()

    logger.info(f"管理员 {current_admin.username} 删除了权限: {permission.code}")
    return {"message": "权限已删除", "id": permission_id}


# ========== Role Endpoints ==========


@router.get("/roles", response_model=dict)
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取所有角色列表"""
    result = await db.execute(
        select(Role).options(selectinload(Role.role_permissions).selectinload(RolePermission.permission))
    )
    roles = result.scalars().all()

    return {
        "roles": [
            {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "is_active": role.is_active,
                "created_at": role.created_at,
                "permission_count": len(role.permissions),
                "permissions": [
                    {"id": p.id, "name": p.name, "code": p.code, "module": p.module} for p in role.permissions
                ],
            }
            for role in roles
        ],
        "total": len(roles),
    }


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取角色详情"""
    result = await db.execute(
        select(Role)
        .where(Role.id == role_id)
        .options(selectinload(Role.role_permissions).selectinload(RolePermission.permission))
    )
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    return role


@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """创建新角色"""
    # 检查名称是否重复
    existing = await db.execute(select(Role).where(Role.name == role.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="角色名称已存在")

    # 创建角色
    new_role = Role(name=role.name, description=role.description, is_active=True)
    db.add(new_role)
    await db.flush()

    # 分配权限
    if role.permission_ids:
        permissions_result = await db.execute(
            select(Permission).where(Permission.id.in_(role.permission_ids))
        )
        permissions = permissions_result.scalars().all()
        # Create RolePermission associations
        for perm in permissions:
            role_perm = RolePermission(role_id=new_role.id, permission_id=perm.id)
            db.add(role_perm)

    await db.commit()
    await db.refresh(new_role)
    # Load the relationships
    await db.execute(
        select(Role)
        .where(Role.id == new_role.id)
        .options(selectinload(Role.role_permissions).selectinload(RolePermission.permission))
    )
    await db.refresh(new_role)

    logger.info(
        f"管理员 {current_admin.username} 创建了角色: {role.name} (权限: {len(role.permission_ids)})"
    )
    return new_role


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """更新角色"""
    result = await db.execute(
        select(Role)
        .where(Role.id == role_id)
        .options(selectinload(Role.role_permissions).selectinload(RolePermission.permission))
    )
    db_role = result.scalar_one_or_none()

    if not db_role:
        raise HTTPException(status_code=404, detail="角色不存在")

    # 更新基本信息
    if role.name is not None:
        # 检查名称是否重复
        existing = await db.execute(select(Role).where(Role.name == role.name, Role.id != role_id))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="角色名称已存在")
        db_role.name = role.name

    if role.description is not None:
        db_role.description = role.description

    # 更新权限
    if role.permission_ids is not None:
        # Delete existing role_permissions
        await db.execute(
            RolePermission.__table__.delete().where(RolePermission.role_id == role_id)
        )
        # Add new role_permissions
        if role.permission_ids:
            permissions_result = await db.execute(
                select(Permission).where(Permission.id.in_(role.permission_ids))
            )
            permissions = permissions_result.scalars().all()
            for perm in permissions:
                role_perm = RolePermission(role_id=role_id, permission_id=perm.id)
                db.add(role_perm)

    await db.commit()
    await db.refresh(db_role)
    # Reload relationships
    result = await db.execute(
        select(Role)
        .where(Role.id == role_id)
        .options(selectinload(Role.role_permissions).selectinload(RolePermission.permission))
    )
    db_role = result.scalar_one()

    logger.info(f"管理员 {current_admin.username} 更新了角色: {db_role.name}")
    return db_role


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """删除角色"""
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    # 检查是否有管理员使用该角色
    admin_count_result = await db.execute(select(AdminUser).where(AdminUser.role_id == role_id))
    if admin_count_result.first():
        raise HTTPException(status_code=400, detail="该角色正在被使用，无法删除")

    await db.delete(role)
    await db.commit()

    logger.info(f"管理员 {current_admin.username} 删除了角色: {role.name}")
    return {"message": "角色已删除", "id": role_id}


# ========== Admin User Role Management ==========


@router.get("/admin-users", response_model=dict)
async def list_admin_users(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """获取所有管理员用户列表"""
    result = await db.execute(select(AdminUser).options(selectinload(AdminUser.role)))
    admins = result.scalars().all()

    return {
        "admin_users": [
            {
                "id": admin.id,
                "username": admin.username,
                "email": admin.email,
                "full_name": admin.full_name,
                "is_active": admin.is_active,
                "is_superadmin": admin.is_superadmin,
                "created_at": admin.created_at,
                "last_login": admin.last_login_at,
                "role": (
                    {"id": admin.role.id, "name": admin.role.name, "description": admin.role.description}
                    if admin.role
                    else None
                ),
            }
            for admin in admins
        ],
        "total": len(admins),
    }


@router.get("/admin-users/{admin_id}", response_model=AdminUserResponse)
async def get_admin_user(
    admin_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """获取管理员详情"""
    result = await db.execute(
        select(AdminUser).where(AdminUser.id == admin_id).options(selectinload(AdminUser.role))
    )
    admin = result.scalar_one_or_none()

    if not admin:
        raise HTTPException(status_code=404, detail="管理员不存在")

    return admin


@router.post("/admin-users/{admin_id}/role")
async def assign_role_to_admin(
    admin_id: int,
    assignment: AdminUserRoleAssignment,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """为管理员分配角色"""
    # 获取管理员
    result = await db.execute(
        select(AdminUser).where(AdminUser.id == admin_id).options(selectinload(AdminUser.role))
    )
    admin = result.scalar_one_or_none()

    if not admin:
        raise HTTPException(status_code=404, detail="管理员不存在")

    if admin.is_superadmin:
        raise HTTPException(status_code=403, detail="超级管理员不需要角色分配")

    # 如果 role_id 为 None，则取消角色分配
    if assignment.role_id is None:
        admin.role_id = None
        await db.commit()
        logger.info(f"管理员 {current_admin.username} 取消了 {admin.username} 的角色分配")
        return {"message": "角色已取消分配", "admin_id": admin_id, "role": None}

    # 获取角色
    role_result = await db.execute(select(Role).where(Role.id == assignment.role_id))
    role = role_result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    # 分配角色
    admin.role_id = role.id
    await db.commit()
    await db.refresh(admin)

    logger.info(f"管理员 {current_admin.username} 为 {admin.username} 分配了角色: {role.name}")

    return {
        "message": "角色分配成功",
        "admin_id": admin_id,
        "role": {"id": role.id, "name": role.name},
    }


@router.delete("/admin-users/{admin_id}/role")
async def remove_role_from_admin(
    admin_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """从管理员移除角色"""
    result = await db.execute(
        select(AdminUser).where(AdminUser.id == admin_id).options(selectinload(AdminUser.role))
    )
    admin = result.scalar_one_or_none()

    if not admin:
        raise HTTPException(status_code=404, detail="管理员不存在")

    if admin.is_superadmin:
        raise HTTPException(status_code=403, detail="超级管理员不需要角色管理")

    # 移除角色
    old_role_id = admin.role_id
    admin.role_id = None
    await db.commit()

    logger.info(f"管理员 {current_admin.username} 从 {admin.username} 移除了角色")

    return {"message": "角色已移除", "admin_id": admin_id, "old_role_id": old_role_id}


# ========== Permission Check Utility ==========


@router.get("/check-permission")
async def check_permission(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """检查当前管理员是否有指定权限（使用权限代码，例如：video.create）"""
    if current_admin.is_superadmin:
        return {"has_permission": True, "reason": "superadmin"}

    # 加载管理员的角色和权限
    result = await db.execute(
        select(AdminUser)
        .where(AdminUser.id == current_admin.id)
        .options(
            selectinload(AdminUser.role)
            .selectinload(Role.role_permissions)
            .selectinload(RolePermission.permission)
        )
    )
    admin = result.scalar_one()

    # 检查权限
    if admin.role:
        for perm in admin.role.permissions:
            if perm.code == code:
                return {"has_permission": True, "reason": f"role: {admin.role.name}"}

    return {"has_permission": False, "reason": "no matching permission"}
