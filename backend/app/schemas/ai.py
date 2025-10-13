from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, validator


class AIProviderBase(BaseModel):
    """AI提供商基础Schema"""

    name: str = Field(..., min_length=1, max_length=100, description="配置名称")
    provider_type: str = Field(..., description="提供商类型: openai, grok, google")
    description: Optional[str] = Field(None, description="配置描述")
    api_key: str = Field(..., min_length=1, description="API密钥")
    base_url: Optional[str] = Field(None, description="API基础URL")
    model_name: str = Field(..., min_length=1, max_length=100, description="模型名称")
    max_tokens: Optional[int] = Field(2048, ge=1, le=128000, description="最大令牌数")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="温度参数")
    top_p: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Top P参数")
    frequency_penalty: Optional[float] = Field(0.0, ge=-2.0, le=2.0, description="频率惩罚")
    presence_penalty: Optional[float] = Field(0.0, ge=-2.0, le=2.0, description="存在惩罚")
    settings: Optional[dict[str, Any]] = Field(default_factory=dict, description="额外设置")
    enabled: bool = Field(True, description="是否启用")
    is_default: bool = Field(False, description="是否为默认配置")

    @validator("provider_type")
    def validate_provider_type(cls, v):
        allowed = ["openai", "grok", "google"]
        if v not in allowed:
            raise ValueError(f"provider_type must be one of {allowed}")
        return v


class AIProviderCreate(AIProviderBase):
    """创建AI提供商配置"""

    pass


class AIProviderUpdate(BaseModel):
    """更新AI提供商配置"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    api_key: Optional[str] = Field(None, min_length=1)
    base_url: Optional[str] = None
    model_name: Optional[str] = Field(None, min_length=1, max_length=100)
    max_tokens: Optional[int] = Field(None, ge=1, le=128000)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    settings: Optional[dict[str, Any]] = None
    enabled: Optional[bool] = None
    is_default: Optional[bool] = None


class AIProviderResponse(AIProviderBase):
    """AI提供商响应Schema"""

    id: int
    total_requests: int
    total_tokens: int
    last_used_at: Optional[datetime]
    last_test_at: Optional[datetime]
    last_test_status: Optional[str]
    last_test_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIProviderListResponse(BaseModel):
    """AI提供商列表响应"""

    total: int
    items: list[AIProviderResponse]


class AITestRequest(BaseModel):
    """AI测试请求"""

    message: str = Field(..., min_length=1, max_length=2000, description="测试消息")
    stream: bool = Field(False, description="是否流式响应")


class AITestResponse(BaseModel):
    """AI测试响应"""

    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    tokens_used: Optional[int] = None
    latency_ms: Optional[int] = None


class AIChatRequest(BaseModel):
    """AI聊天请求"""

    provider_id: int = Field(..., description="提供商ID")
    messages: list[dict[str, str]] = Field(..., description="消息列表")
    stream: bool = Field(False, description="是否流式响应")


class AIChatResponse(BaseModel):
    """AI聊天响应"""

    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    tokens_used: Optional[int] = None
    latency_ms: Optional[int] = None
    model: Optional[str] = None


class AIModelInfo(BaseModel):
    """AI模型信息"""

    id: str
    name: str
    description: Optional[str] = None
    context_window: Optional[int] = None
    max_output_tokens: Optional[int] = None


class AIModelsResponse(BaseModel):
    """AI模型列表响应"""

    provider_type: str
    models: list[AIModelInfo]


class AIUsageStats(BaseModel):
    """AI使用统计"""

    provider_id: int
    provider_name: str
    provider_type: str
    total_requests: int
    total_tokens: int
    last_used_at: Optional[datetime]
    enabled: bool


class AIUsageStatsResponse(BaseModel):
    """AI使用统计响应"""

    stats: list[AIUsageStats]
    total_requests: int
    total_tokens: int
