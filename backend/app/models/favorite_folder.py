"""
收藏夹分组模型
Favorite Folder Model
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.user_activity import Favorite


class FavoriteFolder(Base):
    """收藏夹分组表"""

    __tablename__ = "favorite_folders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # 收藏夹名称
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 描述
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否公开
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否为默认收藏夹
    video_count: Mapped[int] = mapped_column(Integer, default=0)  # 视频数量 (冗余字段,便于查询)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="favorite_folders")
    favorites: Mapped[list[Favorite]] = relationship(
        "Favorite", back_populates="folder", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<FavoriteFolder(id={self.id}, name={self.name}, user_id={self.user_id})>"
        )
