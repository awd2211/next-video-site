"""AI 相关数据模型"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class AIRequestLog(Base):
    """AI 请求日志"""
    __tablename__ = "ai_request_logs"

    id = Column(Integer, primary_key=True, index=True)

    # 提供商信息
    provider_id = Column(Integer, ForeignKey("ai_providers.id", ondelete="SET NULL"), nullable=True)
    provider_type = Column(String(50), nullable=False, index=True)  # openai, grok, google
    model = Column(String(100), nullable=False)

    # 请求信息
    request_type = Column(String(50), default="chat")  # chat, completion, embedding
    prompt = Column(Text, nullable=True)  # 请求内容（可能很长）
    response = Column(Text, nullable=True)  # 响应内容

    # 使用统计
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0, index=True)

    # 性能指标
    response_time = Column(Float, default=0)  # 响应时间（秒）
    status = Column(String(20), default="success")  # success, failed, timeout
    error_message = Column(Text, nullable=True)

    # 成本计算
    estimated_cost = Column(Float, default=0)  # 预估成本（美元）

    # 用户信息
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True)

    # 元数据
    request_metadata = Column(JSON, nullable=True)  # 其他信息（如温度、max_tokens等）
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 关系
    provider = relationship("AIProvider", back_populates="request_logs")


class AIQuota(Base):
    """AI 配额管理"""
    __tablename__ = "ai_quotas"

    id = Column(Integer, primary_key=True, index=True)

    # 配额类型
    quota_type = Column(String(50), default="global")  # global, user, provider
    target_id = Column(Integer, nullable=True)  # 用户ID或提供商ID（根据类型）

    # 配额限制
    daily_request_limit = Column(Integer, nullable=True)  # 每日请求限制
    monthly_request_limit = Column(Integer, nullable=True)  # 每月请求限制
    daily_token_limit = Column(Integer, nullable=True)  # 每日Token限制
    monthly_token_limit = Column(Integer, nullable=True)  # 每月Token限制
    daily_cost_limit = Column(Float, nullable=True)  # 每日成本限制（美元）
    monthly_cost_limit = Column(Float, nullable=True)  # 每月成本限制（美元）

    # 当前使用量（每日重置）
    daily_requests_used = Column(Integer, default=0)
    daily_tokens_used = Column(Integer, default=0)
    daily_cost_used = Column(Float, default=0)

    # 月度使用量（每月重置）
    monthly_requests_used = Column(Integer, default=0)
    monthly_tokens_used = Column(Integer, default=0)
    monthly_cost_used = Column(Float, default=0)

    # 速率限制
    rate_limit_per_minute = Column(Integer, nullable=True)  # 每分钟请求限制
    rate_limit_per_hour = Column(Integer, nullable=True)  # 每小时请求限制

    # 状态
    is_active = Column(Boolean, default=True)

    # 重置时间
    last_daily_reset = Column(DateTime, default=datetime.utcnow)
    last_monthly_reset = Column(DateTime, default=datetime.utcnow)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AITemplate(Base):
    """AI Prompt 模板"""
    __tablename__ = "ai_templates"

    id = Column(Integer, primary_key=True, index=True)

    # 基本信息
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)  # 分类

    # 模板内容
    prompt_template = Column(Text, nullable=False)  # Prompt 模板（支持变量）
    variables = Column(JSON, nullable=True)  # 变量定义

    # 推荐配置
    recommended_provider = Column(String(50), nullable=True)  # 推荐提供商
    recommended_model = Column(String(100), nullable=True)  # 推荐模型
    recommended_temperature = Column(Float, nullable=True)
    recommended_max_tokens = Column(Integer, nullable=True)

    # 使用统计
    usage_count = Column(Integer, default=0)

    # 标签
    tags = Column(String(500), nullable=True)  # 逗号分隔

    # 状态
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)  # 是否公开共享

    # 创建者
    created_by = Column(Integer, ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIPerformanceMetric(Base):
    """AI 性能指标（按小时聚合）"""
    __tablename__ = "ai_performance_metrics"

    id = Column(Integer, primary_key=True, index=True)

    # 维度
    provider_type = Column(String(50), nullable=False, index=True)
    model = Column(String(100), nullable=True)
    hour_bucket = Column(DateTime, nullable=False, index=True)  # 小时时间桶

    # 统计指标
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)

    # 性能统计
    avg_response_time = Column(Float, default=0)
    min_response_time = Column(Float, default=0)
    max_response_time = Column(Float, default=0)
    p50_response_time = Column(Float, default=0)  # 中位数
    p95_response_time = Column(Float, default=0)  # 95分位
    p99_response_time = Column(Float, default=0)  # 99分位

    # Token统计
    total_tokens = Column(Integer, default=0)
    avg_tokens_per_request = Column(Float, default=0)

    # 成本统计
    total_cost = Column(Float, default=0)
    avg_cost_per_request = Column(Float, default=0)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 更新 AIProvider 模型，添加关系
from app.models.ai_config import AIProvider
AIProvider.request_logs = relationship("AIRequestLog", back_populates="provider", cascade="all, delete-orphan")
