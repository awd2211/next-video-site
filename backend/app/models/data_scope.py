"""
数据范围权限模型 / Data Scope Permission Models

支持部门/组织级别的数据隔离
Supports department/organization-level data isolation
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Department(Base):
    """
    部门表 / Department Table
    用于组织管理员的组织结构
    """
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment="部门编码")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 层级关系 / Hierarchy
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("departments.id"), nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=0, comment="层级,0为顶级")
    path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="路径,如 1/2/3")

    # 元数据 / Metadata
    is_active: Mapped[bool] = mapped_column(default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # 关系 / Relationships
    children = relationship("Department", back_populates="parent", remote_side=[id])
    parent = relationship("Department", back_populates="children", remote_side=[parent_id])


class DataScope(Base):
    """
    数据范围权限表 / Data Scope Permission Table
    定义角色的数据访问范围
    """
    __tablename__ = "data_scopes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 关联角色 / Associated role
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), index=True)

    # 数据范围类型 / Data scope type
    scope_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="范围类型: all(全部), department(本部门), department_and_children(本部门及下级), custom(自定义)"
    )

    # 自定义范围(当scope_type=custom时) / Custom scope (when scope_type=custom)
    department_ids: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="部门ID列表,JSON格式,如 [1,2,3]"
    )

    # 资源类型 / Resource type
    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="资源类型: video, user, comment等"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AdminUserDepartment(Base):
    """
    管理员部门关联表 / Admin User Department Association Table
    """
    __tablename__ = "admin_user_departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 管理员 / Admin user
    admin_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("admin_users.id", ondelete="CASCADE"),
        index=True
    )

    # 部门 / Department
    department_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("departments.id", ondelete="CASCADE"),
        index=True
    )

    # 是否主部门 / Is primary department
    is_primary: Mapped[bool] = mapped_column(default=False, comment="是否主要部门")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
