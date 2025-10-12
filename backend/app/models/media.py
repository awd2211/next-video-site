from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class MediaType(str, enum.Enum):
    """媒体类型"""
    IMAGE = "image"
    VIDEO = "video"


class MediaStatus(str, enum.Enum):
    """媒体状态"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class Media(Base):
    """媒体资源模型 - 支持树形文件夹结构"""
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)

    # 基本信息
    title = Column(String(255), nullable=False, index=True, comment="标题")
    description = Column(Text, comment="描述")

    # 文件信息
    filename = Column(String(255), nullable=False, comment="原始文件名")
    file_path = Column(String(512), nullable=False, unique=True, comment="文件存储路径")
    file_size = Column(BigInteger, nullable=False, comment="文件大小(字节)")
    mime_type = Column(String(100), comment="MIME类型")

    # 媒体类型和状态
    media_type = Column(Enum(MediaType), nullable=False, index=True, comment="媒体类型")
    status = Column(
        Enum(MediaStatus),
        nullable=False,
        default=MediaStatus.UPLOADING,
        index=True,
        comment="状态"
    )

    # 图片特定信息
    width = Column(Integer, comment="宽度(像素)")
    height = Column(Integer, comment="高度(像素)")

    # 视频特定信息
    duration = Column(Integer, comment="时长(秒)")
    thumbnail_path = Column(String(512), comment="缩略图路径")

    # URL访问
    url = Column(String(512), comment="访问URL")
    thumbnail_url = Column(String(512), comment="缩略图URL")

    # 🆕 树形结构支持
    parent_id = Column(Integer, ForeignKey("media.id"), nullable=True, index=True, comment="父文件夹ID（NULL表示根目录）")
    is_folder = Column(Boolean, default=False, index=True, comment="是否为文件夹")
    path = Column(String(1024), nullable=True, comment="完整路径（如：/root/folder1/folder2）")

    # 🔄 保留旧字段以向后兼容
    folder = Column(String(255), index=True, comment="文件夹/分类（旧字段，向后兼容）")
    tags = Column(String(512), comment="标签(逗号分隔)")

    # 使用统计
    view_count = Column(Integer, default=0, comment="查看次数")
    download_count = Column(Integer, default=0, comment="下载次数")

    # 上传者信息
    uploader_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False, comment="上传者ID")
    uploader = relationship("AdminUser", back_populates="uploaded_media")

    # 🆕 自引用关系（树形结构）
    parent = relationship("Media", remote_side=[id], backref="children")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 软删除
    is_deleted = Column(Boolean, default=False, index=True, comment="是否已删除")
    deleted_at = Column(DateTime, comment="删除时间")

    def __repr__(self):
        type_str = "Folder" if self.is_folder else self.media_type.value if hasattr(self, 'media_type') else "Unknown"
        return f"<Media(id={self.id}, title='{self.title}', type={type_str}, parent_id={self.parent_id})>"

    def get_full_path(self):
        """获取文件/文件夹的完整路径"""
        if self.path:
            return self.path

        # 递归构建路径
        if self.parent_id is None:
            return f"/{self.title}"
        elif self.parent:
            return f"{self.parent.get_full_path()}/{self.title}"
        return f"/{self.title}"
