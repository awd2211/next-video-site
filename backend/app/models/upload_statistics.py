"""
上传统计模型 - 记录所有上传操作的统计信息
"""

from datetime import datetime
from sqlalchemy import Integer, String, DateTime, BigInteger, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database import Base


class UploadStatistics(Base):
    """上传统计模型"""

    __tablename__ = "upload_statistics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 上传信息
    upload_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True, comment="上传会话ID")
    filename: Mapped[str] = mapped_column(String(255), nullable=False, comment="文件名")
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="文件大小（字节）")
    mime_type: Mapped[str | None] = mapped_column(String(100), comment="MIME 类型")
    upload_type: Mapped[str | None] = mapped_column(String(50), comment="上传类型 (video/poster/backdrop)")

    # 上传者信息
    admin_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("admin_users.id"), nullable=False, comment="上传者ID"
    )
    admin = relationship("AdminUser", foreign_keys=[admin_id])

    # 性能指标
    total_chunks: Mapped[int | None] = mapped_column(Integer, comment="总分片数")
    uploaded_chunks: Mapped[int | None] = mapped_column(Integer, comment="已上传分片数")
    duration_seconds: Mapped[float | None] = mapped_column(Float, comment="上传耗时（秒）")
    upload_speed: Mapped[float | None] = mapped_column(Float, comment="平均上传速度（字节/秒）")

    # 存储信息
    object_name: Mapped[str | None] = mapped_column(String(512), comment="MinIO 对象名称")
    minio_upload_id: Mapped[str | None] = mapped_column(String(255), comment="MinIO multipart upload ID")

    # 状态
    is_success: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否成功")
    error_message: Mapped[str | None] = mapped_column(Text, comment="错误信息")

    # IP 地址
    ip_address: Mapped[str | None] = mapped_column(String(45), comment="上传者 IP 地址")

    # 时间戳
    started_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, comment="开始时间"
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, comment="完成时间")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, comment="记录创建时间"
    )

    def __repr__(self):
        status = "成功" if self.is_success else "失败"
        return f"<UploadStatistics(id={self.id}, filename='{self.filename}', size={self.file_size}, status={status})>"

    def get_upload_speed_mbps(self) -> float:
        """获取上传速度（MB/s）"""
        if self.upload_speed:
            return self.upload_speed / (1024 * 1024)
        return 0.0

    def get_file_size_mb(self) -> float:
        """获取文件大小（MB）"""
        return self.file_size / (1024 * 1024)
