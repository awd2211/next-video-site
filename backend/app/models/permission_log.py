"""
权限审计日志模型
记录所有权限相关的变更操作
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class PermissionLog(Base):
    """权限变更日志"""

    __tablename__ = "permission_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 操作管理员
    admin_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True
    )
    admin_username: Mapped[str] = mapped_column(String(100), nullable=False)

    # 操作类型
    action: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # role_created, role_updated, role_deleted, permissions_assigned, permissions_removed, role_assigned_to_admin, etc.

    # 目标信息
    target_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # role, admin_user, permission
    target_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    target_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # 变更内容
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON格式
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON格式
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 请求信息
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True, nullable=False
    )

    def __repr__(self):
        return f"<PermissionLog {self.action} by {self.admin_username} on {self.target_type}:{self.target_id}>"
