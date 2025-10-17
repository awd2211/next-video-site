"""
媒体文件分享模型
"""
from datetime import datetime
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database import Base


class MediaShare(Base):
    """媒体文件分享链接"""

    __tablename__ = "media_shares"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 分享的媒体文件
    media_id: Mapped[int] = mapped_column(Integer, ForeignKey("media.id", ondelete="CASCADE"), nullable=False, index=True)

    # 分享码（短码，用于URL）
    share_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True, comment="分享码")

    # 访问密码（可选）
    password: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="访问密码（加密后）")

    # 分享设置
    allow_download: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否允许下载")
    max_downloads: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="最大下载次数（null表示无限制）")
    download_count: Mapped[int] = mapped_column(Integer, default=0, comment="已下载次数")

    max_views: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="最大访问次数（null表示无限制）")
    view_count: Mapped[int] = mapped_column(Integer, default=0, comment="已访问次数")

    # 有效期
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="过期时间（null表示永久有效）")

    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, comment="是否启用")

    # 创建者
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("admin_users.id"), nullable=False, comment="创建者ID")

    # 备注
    note: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注说明")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    media = relationship("Media", back_populates="shares")
    creator = relationship("AdminUser", foreign_keys=[created_by])

    def __repr__(self):
        return f"<MediaShare(id={self.id}, code={self.share_code}, media_id={self.media_id})>"

    @property
    def is_expired(self) -> bool:
        """检查是否已过期"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def is_available(self) -> bool:
        """检查是否可用"""
        if not self.is_active:
            return False
        if self.is_expired:
            return False
        if self.max_views and self.view_count >= self.max_views:
            return False
        if self.max_downloads and self.download_count >= self.max_downloads:
            return False
        return True
