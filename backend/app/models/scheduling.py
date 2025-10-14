"""
内容调度系统模型
支持视频、横幅、公告、推荐位等多种内容类型的统一调度管理
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import AdminUser


class ScheduleContentType(str, enum.Enum):
    """调度内容类型"""

    VIDEO = "video"
    BANNER = "banner"
    ANNOUNCEMENT = "announcement"
    RECOMMENDATION = "recommendation"
    SERIES = "series"


class ScheduleStatus(str, enum.Enum):
    """调度状态"""

    PENDING = "pending"  # 等待发布
    PUBLISHED = "published"  # 已发布
    FAILED = "failed"  # 发布失败
    CANCELLED = "cancelled"  # 已取消
    EXPIRED = "expired"  # 已过期（到达end_time）


class PublishStrategy(str, enum.Enum):
    """发布策略"""

    IMMEDIATE = "immediate"  # 立即全量发布
    PROGRESSIVE = "progressive"  # 渐进式发布（逐步扩大用户群）
    REGIONAL = "regional"  # 区域定时发布
    AB_TEST = "ab_test"  # AB测试发布


class ScheduleRecurrence(str, enum.Enum):
    """重复类型"""

    ONCE = "once"  # 一次性
    DAILY = "daily"  # 每日
    WEEKLY = "weekly"  # 每周
    MONTHLY = "monthly"  # 每月


class ContentSchedule(Base):
    """
    统一内容调度表
    支持多种内容类型的定时发布、上下线管理
    """

    __tablename__ = "content_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 内容关联
    content_type: Mapped[ScheduleContentType] = mapped_column(
        Enum(ScheduleContentType), nullable=False, index=True, comment="内容类型"
    )
    content_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, comment="内容ID")

    # 调度时间
    scheduled_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True, comment="计划发布时间"
    )
    actual_publish_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="实际发布时间"
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="结束时间（自动下线）"
    )

    # 状态管理
    status: Mapped[ScheduleStatus] = mapped_column(
        Enum(ScheduleStatus), nullable=False, default=ScheduleStatus.PENDING, index=True, comment="调度状态"
    )
    auto_publish: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否自动发布")
    auto_expire: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否自动过期")

    # 发布策略
    publish_strategy: Mapped[PublishStrategy] = mapped_column(
        Enum(PublishStrategy), nullable=False, default=PublishStrategy.IMMEDIATE, comment="发布策略"
    )
    strategy_config: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default={}, comment="策略配置（如渐进式发布的百分比、区域列表等）"
    )

    # 重复设置
    recurrence: Mapped[ScheduleRecurrence] = mapped_column(
        Enum(ScheduleRecurrence), nullable=False, default=ScheduleRecurrence.ONCE, comment="重复类型"
    )
    recurrence_config: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default={}, comment="重复配置（如每周的星期几、每月的日期等）"
    )
    next_occurrence: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="下次执行时间（用于重复任务）"
    )

    # 通知设置
    notify_subscribers: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否通知订阅者")
    notify_before_minutes: Mapped[int] = mapped_column(Integer, default=0, comment="提前通知分钟数（0表示不提前）")
    notification_sent: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否已发送通知")

    # 条件发布
    condition_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="条件类型（如approval_required, min_views）"
    )
    condition_value: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default={}, comment="条件参数"
    )
    condition_met: Mapped[bool] = mapped_column(Boolean, default=True, comment="条件是否满足")

    # 优先级和排序
    priority: Mapped[int] = mapped_column(Integer, default=0, comment="优先级（数字越大优先级越高）")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")

    # 错误处理
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="错误信息")
    retry_count: Mapped[int] = mapped_column(Integer, default=0, comment="重试次数")
    max_retry: Mapped[int] = mapped_column(Integer, default=3, comment="最大重试次数")

    # 元数据
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="调度任务标题（用于显示）")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="说明")
    tags: Mapped[list[str]] = mapped_column(JSONB, default=[], comment="标签")
    extra_data: Mapped[dict[str, Any]] = mapped_column(JSONB, default={}, comment="额外元数据")

    # 审计字段
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True, comment="创建人"
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True, comment="最后更新人"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creator: Mapped[Optional[AdminUser]] = relationship("AdminUser", foreign_keys=[created_by])
    updater: Mapped[Optional[AdminUser]] = relationship("AdminUser", foreign_keys=[updated_by])

    def __repr__(self):
        return (
            f"<ContentSchedule(id={self.id}, type={self.content_type}, "
            f"content_id={self.content_id}, status={self.status}, "
            f"scheduled_time={self.scheduled_time})>"
        )

    @property
    def is_overdue(self) -> bool:
        """是否已过期"""
        from datetime import timezone as tz

        if self.status != ScheduleStatus.PENDING:
            return False
        return datetime.now(tz.utc) > self.scheduled_time

    @property
    def is_due(self) -> bool:
        """是否到达发布时间"""
        from datetime import timezone as tz

        if self.status != ScheduleStatus.PENDING:
            return False
        return datetime.now(tz.utc) >= self.scheduled_time


class ScheduleTemplate(Base):
    """
    调度模板
    保存常用的发布策略配置，方便快速创建调度任务
    """

    __tablename__ = "schedule_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="模板名称")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="模板描述")

    # 适用的内容类型
    content_types: Mapped[list[str]] = mapped_column(JSONB, default=[], comment="适用的内容类型列表")

    # 模板配置
    publish_strategy: Mapped[PublishStrategy] = mapped_column(Enum(PublishStrategy))
    strategy_config: Mapped[dict[str, Any]] = mapped_column(JSONB, default={})
    recurrence: Mapped[ScheduleRecurrence] = mapped_column(Enum(ScheduleRecurrence))
    recurrence_config: Mapped[dict[str, Any]] = mapped_column(JSONB, default={})

    # 默认通知设置
    notify_subscribers: Mapped[bool] = mapped_column(Boolean, default=False)
    notify_before_minutes: Mapped[int] = mapped_column(Integer, default=0)

    # 使用统计
    usage_count: Mapped[int] = mapped_column(Integer, default=0, comment="使用次数")

    # 审计
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否系统模板")
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creator: Mapped[Optional[AdminUser]] = relationship("AdminUser")


class ScheduleHistory(Base):
    """
    调度历史记录
    记录所有调度操作和结果，用于审计和分析
    """

    __tablename__ = "schedule_histories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    schedule_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("content_schedules.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # 操作信息
    action: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="操作类型（created, published, failed, cancelled, rolled_back）"
    )
    status_before: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="操作前状态")
    status_after: Mapped[str] = mapped_column(String(50), nullable=False, comment="操作后状态")

    # 结果信息
    success: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否成功")
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="消息或错误信息")
    details: Mapped[dict[str, Any]] = mapped_column(JSONB, default={}, comment="详细信息")

    # 执行信息
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    executed_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True, comment="执行人（手动操作时）"
    )
    is_automatic: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否自动执行")

    # 性能指标
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="执行耗时（毫秒）")

    # Relationships
    schedule: Mapped[ContentSchedule] = relationship("ContentSchedule")
    executor: Mapped[Optional[AdminUser]] = relationship("AdminUser")
