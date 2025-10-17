"""AI 相关数据模型"""
from sqlalchemy import Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from app.database import Base


class AIRequestLog(Base):
    """AI 请求日志"""
    __tablename__ = "ai_request_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 提供商信息
    provider_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("ai_providers.id", ondelete="SET NULL"), nullable=True)
    provider_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # openai, grok, google
    model: Mapped[str] = mapped_column(String(100), nullable=False)

    # 请求信息
    request_type: Mapped[str] = mapped_column(String(50), default="chat")  # chat, completion, embedding
    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)  # 请求内容（可能很长）
    response: Mapped[str | None] = mapped_column(Text, nullable=True)  # 响应内容

    # 使用统计
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, index=True)

    # 性能指标
    response_time: Mapped[float] = mapped_column(Float, default=0)  # 响应时间（秒）
    status: Mapped[str] = mapped_column(String(20), default="success")  # success, failed, timeout
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 成本计算
    estimated_cost: Mapped[float] = mapped_column(Float, default=0)  # 预估成本（美元）

    # 用户信息
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    admin_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True)

    # 元数据
    request_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 其他信息（如温度、max_tokens等）
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # 关系
    provider = relationship("AIProvider", back_populates="request_logs")


class AIQuota(Base):
    """AI 配额管理"""
    __tablename__ = "ai_quotas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 配额类型
    quota_type: Mapped[str] = mapped_column(String(50), default="global")  # global, user, provider
    target_id: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 用户ID或提供商ID（根据类型）

    # 配额限制
    daily_request_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 每日请求限制
    monthly_request_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 每月请求限制
    daily_token_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 每日Token限制
    monthly_token_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 每月Token限制
    daily_cost_limit: Mapped[float | None] = mapped_column(Float, nullable=True)  # 每日成本限制（美元）
    monthly_cost_limit: Mapped[float | None] = mapped_column(Float, nullable=True)  # 每月成本限制（美元）

    # 当前使用量（每日重置）
    daily_requests_used: Mapped[int] = mapped_column(Integer, default=0)
    daily_tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    daily_cost_used: Mapped[float] = mapped_column(Float, default=0)

    # 月度使用量（每月重置）
    monthly_requests_used: Mapped[int] = mapped_column(Integer, default=0)
    monthly_tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    monthly_cost_used: Mapped[float] = mapped_column(Float, default=0)

    # 速率限制
    rate_limit_per_minute: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 每分钟请求限制
    rate_limit_per_hour: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 每小时请求限制

    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # 重置时间
    last_daily_reset: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_monthly_reset: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AITemplate(Base):
    """AI Prompt 模板"""
    __tablename__ = "ai_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 基本信息
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)  # 分类

    # 模板内容
    prompt_template: Mapped[str] = mapped_column(Text, nullable=False)  # Prompt 模板（支持变量）
    variables: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 变量定义

    # 推荐配置
    recommended_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)  # 推荐提供商
    recommended_model: Mapped[str | None] = mapped_column(String(100), nullable=True)  # 推荐模型
    recommended_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    recommended_max_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # 使用统计
    usage_count: Mapped[int] = mapped_column(Integer, default=0)

    # 标签
    tags: Mapped[str | None] = mapped_column(String(500), nullable=True)  # 逗号分隔

    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否公开共享

    # 创建者
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIPerformanceMetric(Base):
    """AI 性能指标（按小时聚合）"""
    __tablename__ = "ai_performance_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 维度
    provider_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    hour_bucket: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)  # 小时时间桶

    # 统计指标
    total_requests: Mapped[int] = mapped_column(Integer, default=0)
    successful_requests: Mapped[int] = mapped_column(Integer, default=0)
    failed_requests: Mapped[int] = mapped_column(Integer, default=0)

    # 性能统计
    avg_response_time: Mapped[float] = mapped_column(Float, default=0)
    min_response_time: Mapped[float] = mapped_column(Float, default=0)
    max_response_time: Mapped[float] = mapped_column(Float, default=0)
    p50_response_time: Mapped[float] = mapped_column(Float, default=0)  # 中位数
    p95_response_time: Mapped[float] = mapped_column(Float, default=0)  # 95分位
    p99_response_time: Mapped[float] = mapped_column(Float, default=0)  # 99分位

    # Token统计
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    avg_tokens_per_request: Mapped[float] = mapped_column(Float, default=0)

    # 成本统计
    total_cost: Mapped[float] = mapped_column(Float, default=0)
    avg_cost_per_request: Mapped[float] = mapped_column(Float, default=0)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 更新 AIProvider 模型，添加关系
from app.models.ai_config import AIProvider
AIProvider.request_logs = relationship("AIRequestLog", back_populates="provider", cascade="all, delete-orphan")
