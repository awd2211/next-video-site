"""
Sentry 配置模型
用于管理前端错误监控配置
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.database import Base


class SentryConfig(Base):
    """Sentry 配置表"""

    __tablename__ = "sentry_config"

    id = Column(Integer, primary_key=True, index=True)

    # 基础配置
    dsn = Column(String(500), nullable=False, comment="Sentry DSN")
    environment = Column(String(50), default="production", comment="环境名称")

    # 前端配置
    frontend_enabled = Column(Boolean, default=True, comment="用户前端是否启用")
    admin_frontend_enabled = Column(Boolean, default=True, comment="管理前端是否启用")

    # 采样率配置 (0.0 - 1.0)
    traces_sample_rate = Column(String(10), default="1.0", comment="性能监控采样率")
    replays_session_sample_rate = Column(String(10), default="0.1", comment="会话回放采样率")
    replays_on_error_sample_rate = Column(String(10), default="1.0", comment="错误回放采样率")

    # 过滤配置
    ignore_errors = Column(Text, comment="忽略的错误列表（JSON数组）")
    allowed_urls = Column(Text, comment="允许上报的URL列表（JSON数组）")
    denied_urls = Column(Text, comment="拒绝上报的URL列表（JSON数组）")

    # 附加配置
    release_version = Column(String(100), comment="发布版本号")
    debug_mode = Column(Boolean, default=False, comment="调试模式")
    attach_stacktrace = Column(Boolean, default=True, comment="自动附加堆栈跟踪")

    # 备注
    description = Column(Text, comment="配置说明")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 创建者
    created_by = Column(Integer, comment="创建者管理员ID")
    updated_by = Column(Integer, comment="更新者管理员ID")

    def __repr__(self):
        return f"<SentryConfig(id={self.id}, environment={self.environment})>"
