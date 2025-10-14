"""AI 增强功能相关 Schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============= AI Request Log Schemas =============

class AIRequestLogBase(BaseModel):
    provider_type: str
    model: str
    request_type: Optional[str] = "chat"
    prompt: Optional[str] = None
    response: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    response_time: float = 0
    status: str = "success"
    error_message: Optional[str] = None
    estimated_cost: float = 0
    request_metadata: Optional[Dict[str, Any]] = None


class AIRequestLogCreate(AIRequestLogBase):
    provider_id: Optional[int] = None
    user_id: Optional[int] = None
    admin_user_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AIRequestLogResponse(AIRequestLogBase):
    id: int
    provider_id: Optional[int]
    user_id: Optional[int]
    admin_user_id: Optional[int]
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AIRequestLogQuery(BaseModel):
    """查询参数"""
    provider_type: Optional[str] = None
    model: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[int] = None
    admin_user_id: Optional[int] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=100)


# ============= AI Quota Schemas =============

class AIQuotaBase(BaseModel):
    quota_type: str = "global"  # global, user, provider
    target_id: Optional[int] = None
    daily_request_limit: Optional[int] = None
    monthly_request_limit: Optional[int] = None
    daily_token_limit: Optional[int] = None
    monthly_token_limit: Optional[int] = None
    daily_cost_limit: Optional[float] = None
    monthly_cost_limit: Optional[float] = None
    rate_limit_per_minute: Optional[int] = None
    rate_limit_per_hour: Optional[int] = None
    is_active: bool = True


class AIQuotaCreate(AIQuotaBase):
    pass


class AIQuotaUpdate(BaseModel):
    daily_request_limit: Optional[int] = None
    monthly_request_limit: Optional[int] = None
    daily_token_limit: Optional[int] = None
    monthly_token_limit: Optional[int] = None
    daily_cost_limit: Optional[float] = None
    monthly_cost_limit: Optional[float] = None
    rate_limit_per_minute: Optional[int] = None
    rate_limit_per_hour: Optional[int] = None
    is_active: Optional[bool] = None


class AIQuotaResponse(AIQuotaBase):
    id: int
    daily_requests_used: int
    daily_tokens_used: int
    daily_cost_used: float
    monthly_requests_used: int
    monthly_tokens_used: int
    monthly_cost_used: float
    last_daily_reset: datetime
    last_monthly_reset: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============= AI Template Schemas =============

class AITemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    prompt_template: str = Field(..., min_length=1)
    variables: Optional[Dict[str, Any]] = None
    recommended_provider: Optional[str] = None
    recommended_model: Optional[str] = None
    recommended_temperature: Optional[float] = Field(None, ge=0, le=2)
    recommended_max_tokens: Optional[int] = Field(None, ge=1)
    tags: Optional[str] = None
    is_active: bool = True
    is_public: bool = False


class AITemplateCreate(AITemplateBase):
    pass


class AITemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    prompt_template: Optional[str] = Field(None, min_length=1)
    variables: Optional[Dict[str, Any]] = None
    recommended_provider: Optional[str] = None
    recommended_model: Optional[str] = None
    recommended_temperature: Optional[float] = Field(None, ge=0, le=2)
    recommended_max_tokens: Optional[int] = Field(None, ge=1)
    tags: Optional[str] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None


class AITemplateResponse(AITemplateBase):
    id: int
    usage_count: int
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============= AI Performance Metrics Schemas =============

class AIPerformanceMetricResponse(BaseModel):
    id: int
    provider_type: str
    model: Optional[str]
    hour_bucket: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float
    total_tokens: int
    avg_tokens_per_request: float
    total_cost: float
    avg_cost_per_request: float
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Statistics Schemas =============

class AIUsageStats(BaseModel):
    """AI 使用统计"""
    total_requests: int
    total_tokens: int
    total_cost: float
    avg_response_time: float
    success_rate: float
    requests_by_provider: Dict[str, int]
    tokens_by_provider: Dict[str, int]
    cost_by_provider: Dict[str, float]


class AICostStats(BaseModel):
    """成本统计"""
    today_cost: float
    yesterday_cost: float
    this_month_cost: float
    last_month_cost: float
    cost_trend: List[Dict[str, Any]]  # 每日成本趋势
    cost_by_model: Dict[str, float]
    projected_monthly_cost: float  # 预计本月成本


class AIQuotaStatus(BaseModel):
    """配额状态"""
    quota_type: str
    daily_limit: Optional[int]
    daily_used: int
    daily_remaining: Optional[int]
    monthly_limit: Optional[int]
    monthly_used: int
    monthly_remaining: Optional[int]
    is_exceeded: bool
    warning_level: str  # normal, warning, critical
