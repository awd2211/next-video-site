"""
角色权限管理 API (RBAC - Role-Based Access Control)
支持角色创建、权限分配、管理员角色管理
"""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import select, func
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
    current_admin: AdminUser = Depends(get_current_admin_user),  # 修改：允许所有 admin 查看权限列表
):
    """
    获取所有权限列表
    可选按模块类型筛选
    注意：所有管理员都可以查看权限列表，但只有 superadmin 可以创建/删除权限
    """
    query = select(Permission).order_by(Permission.module, Permission.code)

    if module:
        query = query.where(Permission.module == module)

    result = await db.execute(query)
    permissions = result.scalars().all()

    # 序列化权限列表
    permission_list = [
        {
            "id": perm.id,
            "name": perm.name,
            "code": perm.code,
            "module": perm.module,
            "description": perm.description,
            "created_at": perm.created_at.isoformat() if perm.created_at else None,
        }
        for perm in permissions
    ]

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

    return {"permissions": permission_list, "grouped": grouped, "total": len(permissions)}


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
    current_admin: AdminUser = Depends(get_current_admin_user),  # 修改：允许所有 admin 查看管理员列表
):
    """获取所有管理员用户列表（所有 admin 可查看，仅 superadmin 可修改角色）"""
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


@router.get("/my-permissions")
async def get_my_permissions(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取当前管理员的所有权限"""
    from app.utils.permissions import get_admin_permission_summary

    summary = await get_admin_permission_summary(current_admin.id, db)

    return {
        "admin_id": current_admin.id,
        "username": current_admin.username,
        "is_superadmin": summary["is_superadmin"],
        "role": summary["role"],
        "permissions": summary["permissions"],
        "permission_count": summary["permission_count"]
    }


# ========== Role Templates ==========


@router.get("/role-templates")
async def get_role_templates(
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取角色模板列表"""
    from app.utils.role_templates import get_template_list

    templates = get_template_list()

    return {
        "templates": templates,
        "total": len(templates)
    }


@router.get("/role-templates/{template_key}")
async def get_role_template(
    template_key: str,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取指定角色模板详情"""
    from app.utils.role_templates import get_role_template as get_template, validate_template_permissions

    template = get_template(template_key)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # 获取所有可用权限
    result = await db.execute(select(Permission))
    all_permissions = result.scalars().all()
    available_permission_codes = [p.code for p in all_permissions]

    # 验证模板权限
    validation = validate_template_permissions(template_key, available_permission_codes)

    # 获取权限详情
    permission_details = []
    for perm_code in template["permissions"]:
        perm = next((p for p in all_permissions if p.code == perm_code), None)
        if perm:
            permission_details.append({
                "id": perm.id,
                "code": perm.code,
                "name": perm.name,
                "module": perm.module,
            })

    return {
        "key": template_key,
        "name": template["name"],
        "description": template["description"],
        "permissions": permission_details,
        "permission_count": len(permission_details),
        "icon": template.get("icon", "🔧"),
        "color": template.get("color", "#1890ff"),
        "validation": validation
    }


@router.post("/roles/from-template/{template_key}")
async def create_role_from_template(
    template_key: str,
    role_name: Optional[str] = None,
    role_description: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """从模板创建角色"""
    from app.utils.role_templates import get_role_template as get_template
    from app.utils.permission_logger import log_role_created

    template = get_template(template_key)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # 使用提供的名称或模板默认名称
    final_name = role_name or template["name"]
    final_description = role_description or template["description"]

    # 检查角色名称是否已存在
    existing = await db.execute(select(Role).where(Role.name == final_name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="角色名称已存在")

    # 获取权限ID
    permission_codes = template["permissions"]
    permissions_result = await db.execute(
        select(Permission).where(Permission.code.in_(permission_codes))
    )
    permissions = permissions_result.scalars().all()

    if len(permissions) != len(permission_codes):
        found_codes = {p.code for p in permissions}
        missing = set(permission_codes) - found_codes
        raise HTTPException(
            status_code=400,
            detail=f"部分权限不存在: {', '.join(missing)}"
        )

    # 创建角色
    new_role = Role(
        name=final_name,
        description=final_description,
        is_active=True
    )
    db.add(new_role)
    await db.flush()

    # 分配权限
    for perm in permissions:
        role_perm = RolePermission(role_id=new_role.id, permission_id=perm.id)
        db.add(role_perm)

    await db.commit()
    await db.refresh(new_role)

    # 记录审计日志
    await log_role_created(
        db=db,
        admin=current_admin,
        role_id=new_role.id,
        role_name=new_role.name,
        permissions=permission_codes
    )
    await db.commit()

    logger.info(
        f"管理员 {current_admin.username} 从模板 '{template_key}' 创建了角色: {final_name}"
    )

    return {
        "message": "角色创建成功",
        "role_id": new_role.id,
        "role_name": new_role.name,
        "template_key": template_key,
        "permission_count": len(permissions)
    }


# ========== Permission Audit Logs ==========


@router.get("/permission-logs")
async def get_permission_logs(
    skip: int = 0,
    limit: int = 50,
    action: Optional[str] = None,
    target_type: Optional[str] = None,
    admin_username: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """获取权限变更日志"""
    from app.models.permission_log import PermissionLog

    query = select(PermissionLog).order_by(PermissionLog.created_at.desc())

    # 过滤条件
    if action:
        query = query.where(PermissionLog.action == action)
    if target_type:
        query = query.where(PermissionLog.target_type == target_type)
    if admin_username:
        query = query.where(PermissionLog.admin_username.ilike(f"%{admin_username}%"))

    # 查询总数
    count_query = select(func.count()).select_from(PermissionLog)
    if action:
        count_query = count_query.where(PermissionLog.action == action)
    if target_type:
        count_query = count_query.where(PermissionLog.target_type == target_type)
    if admin_username:
        count_query = count_query.where(PermissionLog.admin_username.ilike(f"%{admin_username}%"))

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页查询
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()

    return {
        "logs": [
            {
                "id": log.id,
                "admin_username": log.admin_username,
                "action": log.action,
                "target_type": log.target_type,
                "target_id": log.target_id,
                "target_name": log.target_name,
                "description": log.description,
                "ip_address": log.ip_address,
                "created_at": log.created_at,
            }
            for log in logs
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }


# ========== Permission Validation and Rules ==========


class PermissionValidationRequest(BaseModel):
    """权限验证请求"""
    permission_codes: List[str]


@router.post("/permissions/validate")
async def validate_permission_set(
    request: PermissionValidationRequest,
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    验证权限组合的有效性
    检查权限冲突、依赖关系和推荐权限
    """
    from app.utils.permission_rules import validate_permissions

    validation_result = validate_permissions(request.permission_codes)

    return {
        **validation_result,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/permissions/rules")
async def get_permission_rules(
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取权限规则配置
    包括冲突规则、依赖规则和推荐规则
    """
    from app.utils.permission_rules import (
        PERMISSION_CONFLICTS,
        PERMISSION_DEPENDENCIES,
        PERMISSION_RECOMMENDATIONS
    )

    return {
        "conflicts": [
            {"permission1": p1, "permission2": p2}
            for p1, p2 in PERMISSION_CONFLICTS
        ],
        "dependencies": [
            {"dependent": dep, "required": req}
            for dep, req in PERMISSION_DEPENDENCIES
        ],
        "recommendations": {
            perm: {"recommended": recs}
            for perm, recs in PERMISSION_RECOMMENDATIONS.items()
        }
    }


@router.get("/permissions/hierarchy")
async def get_permission_hierarchy(
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取权限层级结构"""
    from app.utils.permission_rules import get_permission_hierarchy

    hierarchy = get_permission_hierarchy()

    return {
        "hierarchy": hierarchy,
        "total_modules": len(hierarchy)
    }


@router.get("/permissions/suggest/{role_type}")
async def suggest_permissions_for_role_type(
    role_type: str,
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    根据角色类型推荐权限
    支持的类型: content_creator, content_moderator, user_manager, system_admin, viewer
    """
    from app.utils.permission_rules import suggest_permission_template

    permissions = suggest_permission_template(role_type)

    if not permissions:
        raise HTTPException(
            status_code=404,
            detail=f"未找到角色类型: {role_type}. 支持的类型: content_creator, content_moderator, user_manager, system_admin, viewer"
        )

    return {
        "role_type": role_type,
        "suggested_permissions": permissions,
        "permission_count": len(permissions)
    }


# ========== Batch Operations ==========


class BulkPermissionAssignmentRequest(BaseModel):
    """批量权限分配请求"""
    role_ids: List[int]
    permission_codes: List[str]
    action: str  # "add", "remove", "replace"


@router.post("/permissions/bulk-assign")
async def bulk_assign_permissions(
    request: BulkPermissionAssignmentRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """
    批量权限操作
    - add: 添加权限到角色
    - remove: 从角色移除权限
    - replace: 替换角色的所有权限
    """
    from app.utils.permission_logger import log_role_permissions_changed
    from app.utils.permissions import invalidate_role_permissions_cache

    if request.action not in ["add", "remove", "replace"]:
        raise HTTPException(
            status_code=400,
            detail="action 必须是 'add', 'remove' 或 'replace'"
        )

    # 获取权限
    permissions_result = await db.execute(
        select(Permission).where(Permission.code.in_(request.permission_codes))
    )
    permissions = {p.code: p for p in permissions_result.scalars().all()}

    if len(permissions) != len(request.permission_codes):
        found_codes = set(permissions.keys())
        missing = set(request.permission_codes) - found_codes
        raise HTTPException(
            status_code=400,
            detail=f"部分权限不存在: {', '.join(missing)}"
        )

    affected_roles = []

    for role_id in request.role_ids:
        # 获取角色
        role_result = await db.execute(
            select(Role)
            .where(Role.id == role_id)
            .options(selectinload(Role.role_permissions).selectinload(RolePermission.permission))
        )
        role = role_result.scalar_one_or_none()

        if not role:
            logger.warning(f"角色 {role_id} 不存在，跳过")
            continue

        # 记录旧权限
        old_permissions = [p.code for p in role.permissions]

        if request.action == "replace":
            # 删除所有现有权限
            await db.execute(
                RolePermission.__table__.delete().where(RolePermission.role_id == role_id)
            )
            # 添加新权限
            for perm in permissions.values():
                role_perm = RolePermission(role_id=role_id, permission_id=perm.id)
                db.add(role_perm)

        elif request.action == "add":
            # 获取现有权限ID
            existing_perm_ids = {rp.permission_id for rp in role.role_permissions}
            # 只添加不存在的权限
            for perm in permissions.values():
                if perm.id not in existing_perm_ids:
                    role_perm = RolePermission(role_id=role_id, permission_id=perm.id)
                    db.add(role_perm)

        elif request.action == "remove":
            # 删除指定权限
            perm_ids_to_remove = [p.id for p in permissions.values()]
            await db.execute(
                RolePermission.__table__.delete().where(
                    RolePermission.role_id == role_id,
                    RolePermission.permission_id.in_(perm_ids_to_remove)
                )
            )

        # 刷新以获取新权限
        await db.flush()
        await db.refresh(role)

        # 重新加载权限
        role_result = await db.execute(
            select(Role)
            .where(Role.id == role_id)
            .options(selectinload(Role.role_permissions).selectinload(RolePermission.permission))
        )
        role = role_result.scalar_one()

        new_permissions = [p.code for p in role.permissions]

        # 记录审计日志
        await log_role_permissions_changed(
            db=db,
            admin=current_admin,
            role_id=role.id,
            role_name=role.name,
            old_permissions=old_permissions,
            new_permissions=new_permissions,
            action=request.action
        )

        # 清除缓存
        await invalidate_role_permissions_cache(role_id, db)

        affected_roles.append({
            "role_id": role.id,
            "role_name": role.name,
            "permission_count": len(new_permissions)
        })

    await db.commit()

    logger.info(
        f"管理员 {current_admin.username} 批量{request.action}权限，影响 {len(affected_roles)} 个角色"
    )

    return {
        "message": f"批量权限{request.action}操作成功",
        "action": request.action,
        "affected_roles": affected_roles,
        "total_roles": len(affected_roles)
    }
