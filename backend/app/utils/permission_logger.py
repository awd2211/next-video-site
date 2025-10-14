"""
权限审计日志工具
记录所有权限相关操作
"""

import json
from typing import Any, Dict, Optional
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission_log import PermissionLog
from app.models.user import AdminUser


async def log_permission_change(
    db: AsyncSession,
    admin: AdminUser,
    action: str,
    target_type: str,
    target_id: int,
    target_name: Optional[str] = None,
    old_value: Optional[Any] = None,
    new_value: Optional[Any] = None,
    description: Optional[str] = None,
    request: Optional[Request] = None,
):
    """
    记录权限变更日志

    Args:
        db: 数据库会话
        admin: 操作的管理员
        action: 操作类型 (role_created, role_updated, etc.)
        target_type: 目标类型 (role, admin_user, permission)
        target_id: 目标ID
        target_name: 目标名称
        old_value: 变更前的值
        new_value: 变更后的值
        description: 操作描述
        request: FastAPI请求对象(用于获取IP和User-Agent)
    """
    # 序列化值为JSON
    old_value_json = json.dumps(old_value, ensure_ascii=False) if old_value else None
    new_value_json = json.dumps(new_value, ensure_ascii=False) if new_value else None

    # 获取请求信息
    ip_address = None
    user_agent = None
    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

    # 创建日志记录
    log_entry = PermissionLog(
        admin_user_id=admin.id,
        admin_username=admin.username,
        action=action,
        target_type=target_type,
        target_id=target_id,
        target_name=target_name,
        old_value=old_value_json,
        new_value=new_value_json,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    db.add(log_entry)
    await db.flush()


# 常用的日志记录函数

async def log_role_created(
    db: AsyncSession,
    admin: AdminUser,
    role_id: int,
    role_name: str,
    permissions: list,
    request: Optional[Request] = None,
):
    """记录角色创建"""
    await log_permission_change(
        db=db,
        admin=admin,
        action="role_created",
        target_type="role",
        target_id=role_id,
        target_name=role_name,
        new_value={"name": role_name, "permissions": permissions},
        description=f"创建角色 '{role_name}'，包含 {len(permissions)} 个权限",
        request=request,
    )


async def log_role_updated(
    db: AsyncSession,
    admin: AdminUser,
    role_id: int,
    role_name: str,
    old_permissions: list,
    new_permissions: list,
    request: Optional[Request] = None,
):
    """记录角色更新"""
    added = set(new_permissions) - set(old_permissions)
    removed = set(old_permissions) - set(new_permissions)

    description = f"更新角色 '{role_name}'"
    if added:
        description += f"，新增 {len(added)} 个权限"
    if removed:
        description += f"，移除 {len(removed)} 个权限"

    await log_permission_change(
        db=db,
        admin=admin,
        action="role_updated",
        target_type="role",
        target_id=role_id,
        target_name=role_name,
        old_value={"permissions": old_permissions},
        new_value={"permissions": new_permissions, "added": list(added), "removed": list(removed)},
        description=description,
        request=request,
    )


async def log_role_deleted(
    db: AsyncSession,
    admin: AdminUser,
    role_id: int,
    role_name: str,
    permissions: list,
    request: Optional[Request] = None,
):
    """记录角色删除"""
    await log_permission_change(
        db=db,
        admin=admin,
        action="role_deleted",
        target_type="role",
        target_id=role_id,
        target_name=role_name,
        old_value={"name": role_name, "permissions": permissions},
        description=f"删除角色 '{role_name}'",
        request=request,
    )


async def log_admin_role_assigned(
    db: AsyncSession,
    admin: AdminUser,
    target_admin_id: int,
    target_admin_username: str,
    old_role: Optional[str],
    new_role: Optional[str],
    request: Optional[Request] = None,
):
    """记录管理员角色分配"""
    if old_role and new_role:
        description = f"将管理员 '{target_admin_username}' 的角色从 '{old_role}' 变更为 '{new_role}'"
    elif new_role:
        description = f"为管理员 '{target_admin_username}' 分配角色 '{new_role}'"
    else:
        description = f"移除管理员 '{target_admin_username}' 的角色 '{old_role}'"

    await log_permission_change(
        db=db,
        admin=admin,
        action="admin_role_assigned",
        target_type="admin_user",
        target_id=target_admin_id,
        target_name=target_admin_username,
        old_value={"role": old_role},
        new_value={"role": new_role},
        description=description,
        request=request,
    )


async def log_permissions_bulk_assigned(
    db: AsyncSession,
    admin: AdminUser,
    role_ids: list,
    permission_ids: list,
    request: Optional[Request] = None,
):
    """记录批量权限分配"""
    await log_permission_change(
        db=db,
        admin=admin,
        action="permissions_bulk_assigned",
        target_type="role",
        target_id=0,  # 批量操作，没有单个ID
        description=f"批量为 {len(role_ids)} 个角色分配 {len(permission_ids)} 个权限",
        new_value={"role_ids": role_ids, "permission_ids": permission_ids},
        request=request,
    )


async def log_role_permissions_changed(
    db: AsyncSession,
    admin: AdminUser,
    role_id: int,
    role_name: str,
    old_permissions: list,
    new_permissions: list,
    action: str = "update",
    request: Optional[Request] = None,
):
    """记录角色权限变更(用于批量操作)"""
    added = set(new_permissions) - set(old_permissions)
    removed = set(old_permissions) - set(new_permissions)

    action_map = {
        "add": "添加权限",
        "remove": "移除权限",
        "replace": "替换权限"
    }
    action_desc = action_map.get(action, "更新权限")

    description = f"{action_desc}到角色 '{role_name}'"
    if added:
        description += f"，新增 {len(added)} 个"
    if removed:
        description += f"，移除 {len(removed)} 个"

    await log_permission_change(
        db=db,
        admin=admin,
        action=f"role_permissions_{action}",
        target_type="role",
        target_id=role_id,
        target_name=role_name,
        old_value={"permissions": old_permissions},
        new_value={"permissions": new_permissions, "added": list(added), "removed": list(removed)},
        description=description,
        request=request,
    )
