"""
Sentry 配置相关的 Pydantic schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class SentryConfigBase(BaseModel):
    """Sentry 配置基础模型"""

    dsn: str = Field(..., description="Sentry DSN")
    environment: str = Field(default="production", description="环境名称")
    frontend_enabled: bool = Field(default=True, description="用户前端是否启用")
    admin_frontend_enabled: bool = Field(default=True, description="管理前端是否启用")
    traces_sample_rate: str = Field(default="1.0", description="性能监控采样率")
    replays_session_sample_rate: str = Field(default="0.1", description="会话回放采样率")
    replays_on_error_sample_rate: str = Field(default="1.0", description="错误回放采样率")
    ignore_errors: Optional[str] = Field(None, description="忽略的错误列表（JSON数组）")
    allowed_urls: Optional[str] = Field(None, description="允许上报的URL列表（JSON数组）")
    denied_urls: Optional[str] = Field(None, description="拒绝上报的URL列表（JSON数组）")
    release_version: Optional[str] = Field(None, description="发布版本号")
    debug_mode: bool = Field(default=False, description="调试模式")
    attach_stacktrace: bool = Field(default=True, description="自动附加堆栈跟踪")
    description: Optional[str] = Field(None, description="配置说明")

    @validator("traces_sample_rate", "replays_session_sample_rate", "replays_on_error_sample_rate")
    def validate_sample_rate(cls, v):
        """验证采样率在 0.0-1.0 之间"""
        try:
            rate = float(v)
            if not 0.0 <= rate <= 1.0:
                raise ValueError("采样率必须在 0.0 到 1.0 之间")
            return str(rate)
        except ValueError:
            raise ValueError("采样率必须是有效的数字")


class SentryConfigCreate(SentryConfigBase):
    """创建 Sentry 配置"""

    pass


class SentryConfigUpdate(BaseModel):
    """更新 Sentry 配置"""

    dsn: Optional[str] = None
    environment: Optional[str] = None
    frontend_enabled: Optional[bool] = None
    admin_frontend_enabled: Optional[bool] = None
    traces_sample_rate: Optional[str] = None
    replays_session_sample_rate: Optional[str] = None
    replays_on_error_sample_rate: Optional[str] = None
    ignore_errors: Optional[str] = None
    allowed_urls: Optional[str] = None
    denied_urls: Optional[str] = None
    release_version: Optional[str] = None
    debug_mode: Optional[bool] = None
    attach_stacktrace: Optional[bool] = None
    description: Optional[str] = None

    @validator("traces_sample_rate", "replays_session_sample_rate", "replays_on_error_sample_rate")
    def validate_sample_rate(cls, v):
        """验证采样率在 0.0-1.0 之间"""
        if v is None:
            return v
        try:
            rate = float(v)
            if not 0.0 <= rate <= 1.0:
                raise ValueError("采样率必须在 0.0 到 1.0 之间")
            return str(rate)
        except ValueError:
            raise ValueError("采样率必须是有效的数字")


class SentryConfigResponse(SentryConfigBase):
    """Sentry 配置响应"""

    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class SentryConfigPublic(BaseModel):
    """Sentry 公开配置（用于前端获取）"""

    dsn: str
    environment: str
    traces_sample_rate: str
    replays_session_sample_rate: str
    replays_on_error_sample_rate: str
    release_version: Optional[str] = None
    debug_mode: bool
    attach_stacktrace: bool
    ignore_errors: Optional[str] = None
    allowed_urls: Optional[str] = None
    denied_urls: Optional[str] = None

    class Config:
        from_attributes = True
