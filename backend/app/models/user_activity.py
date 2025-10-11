from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Favorite(Base):
    """User favorite videos"""

    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    video_id = Column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    folder_id = Column(
        Integer,
        ForeignKey("favorite_folders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )  # 🆕 收藏夹分组
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="favorites")
    video = relationship("Video", back_populates="favorites")
    folder = relationship("FavoriteFolder", back_populates="favorites")  # 🆕 关联收藏夹


class WatchHistory(Base):
    """User watch history"""

    __tablename__ = "watch_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    video_id = Column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    watch_duration = Column(Integer, default=0)  # in seconds
    last_position = Column(Integer, default=0)  # in seconds
    is_completed = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="watch_history")
    video = relationship("Video", back_populates="watch_history")
