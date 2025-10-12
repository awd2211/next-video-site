"""
上传会话模型 - 支持分块上传和断点续传
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class UploadSession(Base):
    """上传会话模型"""
    __tablename__ = "upload_sessions"

    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(String(64), unique=True, nullable=False, index=True, comment="上传会话ID（UUID）")

    # 文件信息
    filename = Column(String(255), nullable=False, comment="原始文件名")
    file_size = Column(BigInteger, nullable=False, comment="文件总大小（字节）")
    mime_type = Column(String(100), comment="MIME类型")

    # 上传配置
    chunk_size = Column(Integer, default=5242880, comment="分块大小（默认5MB）")
    total_chunks = Column(Integer, nullable=False, comment="总分块数")
    uploaded_chunks = Column(JSON, default=list, comment="已上传的分块索引列表")

    # 目标信息
    title = Column(String(255), nullable=False, comment="媒体标题")
    description = Column(String(1000), comment="媒体描述")
    parent_id = Column(Integer, ForeignKey("media.id"), nullable=True, comment="父文件夹ID")
    tags = Column(String(512), comment="标签")

    # 临时存储路径
    temp_dir = Column(String(512), nullable=False, comment="临时分块存储目录")

    # 状态
    is_completed = Column(Boolean, default=False, comment="是否完成")
    is_merged = Column(Boolean, default=False, comment="是否已合并")

    # 关联信息
    uploader_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False, comment="上传者ID")
    media_id = Column(Integer, ForeignKey("media.id"), nullable=True, comment="完成后的媒体ID")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="最后更新时间")
    expires_at = Column(DateTime, nullable=False, comment="过期时间")

    # 关系
    uploader = relationship("AdminUser")
    media = relationship("Media", foreign_keys=[media_id])

    def __repr__(self):
        return f"<UploadSession(id={self.upload_id}, filename='{self.filename}', progress={len(self.uploaded_chunks)}/{self.total_chunks})>"

    def get_progress(self):
        """获取上传进度百分比"""
        if self.total_chunks == 0:
            return 0
        return (len(self.uploaded_chunks) / self.total_chunks) * 100

    def is_chunk_uploaded(self, chunk_index):
        """检查某个分块是否已上传"""
        return chunk_index in self.uploaded_chunks

    def mark_chunk_uploaded(self, chunk_index):
        """标记某个分块为已上传"""
        if not self.is_chunk_uploaded(chunk_index):
            self.uploaded_chunks.append(chunk_index)
            self.uploaded_chunks.sort()

    def is_upload_complete(self):
        """检查所有分块是否已上传"""
        return len(self.uploaded_chunks) == self.total_chunks
