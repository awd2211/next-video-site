from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text, Enum as SQLEnum, Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
import enum

from app.database import Base


class AIProviderType(str, enum.Enum):
    """AI提供商类型"""

    OPENAI = "openai"
    GROK = "grok"
    GOOGLE = "google"


class AIProvider(Base):
    """AI提供商配置表"""

    __tablename__ = "ai_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 基本信息
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="配置名称")
    provider_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="提供商类型", index=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="配置描述")

    # API配置
    api_key: Mapped[str] = mapped_column(String(500), nullable=False, comment="API密钥(加密存储)")
    base_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="API基础URL(可选)"
    )
    model_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="模型名称"
    )

    # 模型参数
    max_tokens: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=2048, comment="最大令牌数"
    )
    temperature: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, default=0.7, comment="温度参数"
    )
    top_p: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, default=1.0, comment="Top P参数"
    )
    frequency_penalty: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, default=0.0, comment="频率惩罚"
    )
    presence_penalty: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, default=0.0, comment="存在惩罚"
    )

    # 高级设置
    settings: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True, default=dict, comment="额外设置(JSON)"
    )

    # 状态
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="是否启用")
    is_default: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="是否为默认配置"
    )

    # 使用统计
    total_requests: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="总请求次数"
    )
    total_tokens: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="总令牌使用量"
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后使用时间"
    )

    # 测试状态
    last_test_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后测试时间"
    )
    last_test_status: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="最后测试状态: success/failed"
    )
    last_test_message: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="最后测试消息"
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<AIProvider {self.name} ({self.provider_type})>"
