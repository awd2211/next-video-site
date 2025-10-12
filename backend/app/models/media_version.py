"""
媒体文件版本历史模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, BigInteger, Text
from sqlalchemy.orm import relationship

from app.database import Base


class MediaVersion(Base):
    """媒体文件版本历史"""

    __tablename__ = "media_versions"

    id = Column(Integer, primary_key=True, index=True)

    # 关联的媒体文件
    media_id = Column(Integer, ForeignKey("media.id", ondelete="CASCADE"), nullable=False, index=True)

    # 版本信息
    version_number = Column(Integer, nullable=False, comment="版本号")
    file_path = Column(String(512), nullable=False, comment="文件存储路径")
    file_size = Column(BigInteger, nullable=False, comment="文件大小(字节)")
    mime_type = Column(String(100), comment="MIME类型")
    url = Column(String(512), comment="访问URL")

    # 图片/视频属性
    width = Column(Integer, comment="宽度(像素)")
    height = Column(Integer, comment="高度(像素)")
    duration = Column(Integer, comment="时长(秒)")

    # 变更记录
    change_note = Column(Text, comment="变更说明")
    created_by = Column(Integer, ForeignKey("admin_users.id"), nullable=False, comment="上传者ID")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    media = relationship("Media", back_populates="versions")
    creator = relationship("AdminUser", foreign_keys=[created_by])

    def __repr__(self):
        return f"<MediaVersion(id={self.id}, media_id={self.media_id}, version={self.version_number})>"
