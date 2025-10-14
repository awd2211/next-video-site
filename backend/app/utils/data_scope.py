"""
数据范围权限工具 / Data Scope Permission Utilities

提供数据范围权限检查和过滤功能
Provides data scope permission checking and filtering
"""

import json
from typing import List, Optional, Set
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import AdminUser
from app.models.data_scope import Department, DataScope, AdminUserDepartment


async def get_admin_departments(
    admin_id: int,
    db: AsyncSession
) -> List[int]:
    """
    获取管理员所属的所有部门ID
    Get all department IDs for an admin

    Args:
        admin_id: 管理员ID / Admin ID
        db: 数据库会话 / Database session

    Returns:
        List[int]: 部门ID列表 / List of department IDs
    """
    result = await db.execute(
        select(AdminUserDepartment.department_id)
        .where(AdminUserDepartment.admin_user_id == admin_id)
    )
    department_ids = [row[0] for row in result.all()]
    return department_ids


async def get_admin_primary_department(
    admin_id: int,
    db: AsyncSession
) -> Optional[int]:
    """
    获取管理员的主要部门ID
    Get admin's primary department ID

    Args:
        admin_id: 管理员ID / Admin ID
        db: 数据库会话 / Database session

    Returns:
        Optional[int]: 主要部门ID / Primary department ID
    """
    result = await db.execute(
        select(AdminUserDepartment.department_id)
        .where(
            AdminUserDepartment.admin_user_id == admin_id,
            AdminUserDepartment.is_primary == True
        )
    )
    row = result.first()
    return row[0] if row else None


async def get_department_children(
    department_id: int,
    db: AsyncSession,
    include_self: bool = True
) -> List[int]:
    """
    获取部门及其所有子部门ID
    Get department and all its children department IDs

    Args:
        department_id: 部门ID / Department ID
        db: 数据库会话 / Database session
        include_self: 是否包含自身 / Whether to include self

    Returns:
        List[int]: 部门ID列表 / List of department IDs
    """
    # 获取部门路径
    result = await db.execute(
        select(Department).where(Department.id == department_id)
    )
    department = result.scalar_one_or_none()

    if not department:
        return []

    # 查找所有以该部门路径开头的部门(即子部门)
    path_prefix = f"{department.path}/{department.id}" if department.path else str(department.id)

    result = await db.execute(
        select(Department.id).where(Department.path.startswith(path_prefix))
    )
    children_ids = [row[0] for row in result.all()]

    if include_self:
        children_ids.insert(0, department_id)

    return children_ids


async def get_role_data_scope(
    role_id: int,
    resource_type: str,
    db: AsyncSession
) -> Optional[DataScope]:
    """
    获取角色的数据范围配置
    Get role's data scope configuration

    Args:
        role_id: 角色ID / Role ID
        resource_type: 资源类型 / Resource type (video, user, comment, etc.)
        db: 数据库会话 / Database session

    Returns:
        Optional[DataScope]: 数据范围配置 / Data scope configuration
    """
    result = await db.execute(
        select(DataScope).where(
            DataScope.role_id == role_id,
            DataScope.resource_type == resource_type
        )
    )
    return result.scalar_one_or_none()


async def get_admin_accessible_department_ids(
    admin: AdminUser,
    resource_type: str,
    db: AsyncSession
) -> Optional[Set[int]]:
    """
    获取管理员可访问的部门ID集合
    Get the set of department IDs accessible to the admin

    Args:
        admin: 管理员对象 / Admin user object
        resource_type: 资源类型 / Resource type
        db: 数据库会话 / Database session

    Returns:
        Optional[Set[int]]: 部门ID集合。None表示无限制(全部数据)
                           / Set of department IDs. None means no restriction (all data)
    """
    # 超级管理员无限制
    if admin.is_superadmin:
        return None

    # 无角色则无权限
    if not admin.role_id:
        return set()

    # 获取角色的数据范围配置
    data_scope = await get_role_data_scope(admin.role_id, resource_type, db)

    if not data_scope:
        # 无配置则默认为全部数据
        return None

    scope_type = data_scope.scope_type

    if scope_type == "all":
        # 全部数据
        return None

    # 获取管理员所属部门
    admin_departments = await get_admin_departments(admin.id, db)

    if not admin_departments:
        # 管理员未分配部门，无权访问任何数据
        return set()

    if scope_type == "department":
        # 仅本部门
        return set(admin_departments)

    elif scope_type == "department_and_children":
        # 本部门及所有子部门
        accessible_ids = set()
        for dept_id in admin_departments:
            children = await get_department_children(dept_id, db, include_self=True)
            accessible_ids.update(children)
        return accessible_ids

    elif scope_type == "custom":
        # 自定义部门列表
        if data_scope.department_ids:
            try:
                custom_ids = json.loads(data_scope.department_ids)
                return set(custom_ids)
            except json.JSONDecodeError:
                return set()
        return set()

    # 默认无权限
    return set()


async def check_data_scope_permission(
    admin: AdminUser,
    resource_type: str,
    resource_department_id: int,
    db: AsyncSession
) -> bool:
    """
    检查管理员是否有权访问指定部门的资源
    Check if admin has permission to access resources of specified department

    Args:
        admin: 管理员对象 / Admin user object
        resource_type: 资源类型 / Resource type
        resource_department_id: 资源所属部门ID / Resource's department ID
        db: 数据库会话 / Database session

    Returns:
        bool: 是否有权限 / Whether has permission
    """
    accessible_dept_ids = await get_admin_accessible_department_ids(admin, resource_type, db)

    # None表示无限制
    if accessible_dept_ids is None:
        return True

    # 检查资源部门是否在可访问部门列表中
    return resource_department_id in accessible_dept_ids


def build_data_scope_filter(
    admin: AdminUser,
    resource_type: str,
    accessible_dept_ids: Optional[Set[int]],
    department_field_name: str = "department_id"
):
    """
    构建数据范围过滤条件(用于SQLAlchemy查询)
    Build data scope filter condition (for SQLAlchemy query)

    Args:
        admin: 管理员对象 / Admin user object
        resource_type: 资源类型 / Resource type
        accessible_dept_ids: 可访问的部门ID集合(来自get_admin_accessible_department_ids)
                           / Set of accessible department IDs (from get_admin_accessible_department_ids)
        department_field_name: 数据表中部门字段名称 / Department field name in the table

    Returns:
        SQLAlchemy filter condition or None (无限制)

    Example:
        ```python
        from sqlalchemy import select
        from app.models.video import Video

        accessible_dept_ids = await get_admin_accessible_department_ids(admin, "video", db)
        query = select(Video)

        filter_condition = build_data_scope_filter(admin, "video", accessible_dept_ids)
        if filter_condition is not None:
            query = query.where(filter_condition)

        result = await db.execute(query)
        videos = result.scalars().all()
        ```
    """
    # None表示无限制
    if accessible_dept_ids is None:
        return None

    # 空集合表示无权限，返回永假条件
    if not accessible_dept_ids:
        return False  # 这将使查询返回空结果

    # 返回IN条件
    # 注意: 需要在调用处使用getattr获取实际的模型字段
    # 例如: query.where(Video.department_id.in_(accessible_dept_ids))
    return accessible_dept_ids


async def assign_admin_to_department(
    admin_id: int,
    department_id: int,
    is_primary: bool,
    db: AsyncSession
):
    """
    将管理员分配到部门
    Assign admin to department

    Args:
        admin_id: 管理员ID / Admin ID
        department_id: 部门ID / Department ID
        is_primary: 是否为主部门 / Whether is primary department
        db: 数据库会话 / Database session
    """
    # 检查是否已存在
    result = await db.execute(
        select(AdminUserDepartment).where(
            AdminUserDepartment.admin_user_id == admin_id,
            AdminUserDepartment.department_id == department_id
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        # 更新is_primary
        existing.is_primary = is_primary
    else:
        # 创建新关联
        association = AdminUserDepartment(
            admin_user_id=admin_id,
            department_id=department_id,
            is_primary=is_primary
        )
        db.add(association)

    # 如果设置为主部门，取消其他主部门
    if is_primary:
        await db.execute(
            AdminUserDepartment.__table__.update()
            .where(
                AdminUserDepartment.admin_user_id == admin_id,
                AdminUserDepartment.department_id != department_id
            )
            .values(is_primary=False)
        )

    await db.flush()


async def remove_admin_from_department(
    admin_id: int,
    department_id: int,
    db: AsyncSession
):
    """
    将管理员从部门移除
    Remove admin from department

    Args:
        admin_id: 管理员ID / Admin ID
        department_id: 部门ID / Department ID
        db: 数据库会话 / Database session
    """
    await db.execute(
        AdminUserDepartment.__table__.delete().where(
            AdminUserDepartment.admin_user_id == admin_id,
            AdminUserDepartment.department_id == department_id
        )
    )
    await db.flush()
