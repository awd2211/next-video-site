"""
收藏夹分组模型
Favorite Folder Model
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class FavoriteFolder(Base):
    """收藏夹分组表"""

    __tablename__ = "favorite_folders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)  # 收藏夹名称
    description = Column(Text, nullable=True)  # 描述
    is_public = Column(Boolean, default=False)  # 是否公开
    is_default = Column(Boolean, default=False)  # 是否为默认收藏夹
    video_count = Column(Integer, default=0)  # 视频数量 (冗余字段,便于查询)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="favorite_folders")
    favorites = relationship("Favorite", back_populates="folder", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FavoriteFolder(id={self.id}, name={self.name}, user_id={self.user_id})>"
