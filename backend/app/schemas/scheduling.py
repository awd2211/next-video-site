"""
内容调度系统 - Pydantic 验证模式
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.scheduling import (
    PublishStrategy,
    ScheduleContentType,
    ScheduleRecurrence,
    ScheduleStatus,
)


# ========== 基础模式 ==========


class ScheduleBase(BaseModel):
    """调度基础模式"""

    content_type: ScheduleContentType
    content_id: int = Field(..., gt=0)
    scheduled_time: datetime
    end_time: Optional[datetime] = None
    auto_publish: bool = True
    auto_expire: bool = False
    publish_strategy: PublishStrategy = PublishStrategy.IMMEDIATE
    strategy_config: dict[str, Any] = Field(default_factory=dict)
    recurrence: ScheduleRecurrence = ScheduleRecurrence.ONCE
    recurrence_config: dict[str, Any] = Field(default_factory=dict)
    notify_subscribers: bool = False
    notify_before_minutes: int = Field(default=0, ge=0, le=1440)  # 最多提前24小时
    condition_type: Optional[str] = None
    condition_value: dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=0, ge=0, le=100)
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    extra_data: dict[str, Any] = Field(default_factory=dict)

    @field_validator("scheduled_time")
    @classmethod
    def validate_scheduled_time(cls, v: datetime) -> datetime:
        """验证计划时间必须是未来时间"""
        from datetime import timezone

        now = datetime.now(timezone.utc)
        if v <= now:
            raise ValueError("scheduled_time must be in the future")
        return v

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """验证结束时间必须晚于开始时间"""
        if v is not None:
            scheduled_time = info.data.get("scheduled_time")
            if scheduled_time and v <= scheduled_time:
                raise ValueError("end_time must be after scheduled_time")
        return v


class ScheduleCreate(ScheduleBase):
    """创建调度请求"""

    pass


class ScheduleUpdate(BaseModel):
    """更新调度请求"""

    scheduled_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    auto_publish: Optional[bool] = None
    auto_expire: Optional[bool] = None
    publish_strategy: Optional[PublishStrategy] = None
    strategy_config: Optional[dict[str, Any]] = None
    recurrence: Optional[ScheduleRecurrence] = None
    recurrence_config: Optional[dict[str, Any]] = None
    notify_subscribers: Optional[bool] = None
    notify_before_minutes: Optional[int] = Field(None, ge=0, le=1440)
    condition_type: Optional[str] = None
    condition_value: Optional[dict[str, Any]] = None
    priority: Optional[int] = Field(None, ge=0, le=100)
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    extra_data: Optional[dict[str, Any]] = None


class ScheduleResponse(ScheduleBase):
    """调度响应"""

    id: int
    status: ScheduleStatus
    actual_publish_time: Optional[datetime] = None
    next_occurrence: Optional[datetime] = None
    notification_sent: bool
    condition_met: bool
    error_message: Optional[str] = None
    retry_count: int
    max_retry: int
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # 计算属性
    is_overdue: bool = False
    is_due: bool = False

    model_config = {"from_attributes": True}


class ScheduleListResponse(BaseModel):
    """调度列表响应"""

    items: list[ScheduleResponse]
    total: int
    skip: int
    limit: int


# ========== 批量操作 ==========


class BatchScheduleCreate(BaseModel):
    """批量创建调度"""

    schedules: list[ScheduleCreate] = Field(..., min_length=1, max_length=100)


class BatchScheduleUpdate(BaseModel):
    """批量更新调度"""

    schedule_ids: list[int] = Field(..., min_length=1, max_length=100)
    updates: ScheduleUpdate


class BatchOperationResponse(BaseModel):
    """批量操作响应"""

    success_count: int
    failed_count: int
    errors: list[dict[str, Any]] = Field(default_factory=list)


# ========== 模板相关 ==========


class TemplateBase(BaseModel):
    """模板基础模式"""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    content_types: list[str] = Field(default_factory=list)
    publish_strategy: PublishStrategy = PublishStrategy.IMMEDIATE
    strategy_config: dict[str, Any] = Field(default_factory=dict)
    recurrence: ScheduleRecurrence = ScheduleRecurrence.ONCE
    recurrence_config: dict[str, Any] = Field(default_factory=dict)
    notify_subscribers: bool = False
    notify_before_minutes: int = Field(default=0, ge=0, le=1440)


class TemplateCreate(TemplateBase):
    """创建模板请求"""

    pass


class TemplateUpdate(BaseModel):
    """更新模板请求"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    content_types: Optional[list[str]] = None
    publish_strategy: Optional[PublishStrategy] = None
    strategy_config: Optional[dict[str, Any]] = None
    recurrence: Optional[ScheduleRecurrence] = None
    recurrence_config: Optional[dict[str, Any]] = None
    notify_subscribers: Optional[bool] = None
    notify_before_minutes: Optional[int] = Field(None, ge=0, le=1440)
    is_active: Optional[bool] = None


class TemplateResponse(TemplateBase):
    """模板响应"""

    id: int
    usage_count: int
    is_active: bool
    is_system: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TemplateApply(BaseModel):
    """应用模板请求"""

    template_id: int
    content_type: ScheduleContentType
    content_id: int
    scheduled_time: datetime
    # 可以覆盖模板的某些设置
    override_title: Optional[str] = None
    override_priority: Optional[int] = Field(None, ge=0, le=100)


# ========== 历史记录 ==========


class HistoryResponse(BaseModel):
    """历史记录响应"""

    id: int
    schedule_id: int
    action: str
    status_before: Optional[str] = None
    status_after: str
    success: bool
    message: Optional[str] = None
    details: dict[str, Any]
    executed_at: datetime
    executed_by: Optional[int] = None
    is_automatic: bool
    execution_time_ms: Optional[int] = None

    model_config = {"from_attributes": True}


# ========== 统计信息 ==========


class SchedulingStats(BaseModel):
    """调度统计"""

    pending_count: int = 0
    published_today: int = 0
    published_this_week: int = 0
    failed_count: int = 0
    overdue_count: int = 0
    upcoming_24h: int = 0
    by_content_type: dict[str, int] = Field(default_factory=dict)
    by_status: dict[str, int] = Field(default_factory=dict)
    by_strategy: dict[str, int] = Field(default_factory=dict)


class SchedulingAnalytics(BaseModel):
    """调度分析"""

    success_rate: float = 0.0
    avg_execution_time_ms: float = 0.0
    peak_hours: list[int] = Field(default_factory=list)  # 发布高峰时段
    best_performing_strategy: Optional[str] = None
    weekly_trends: dict[str, list[int]] = Field(default_factory=dict)


class CalendarEvent(BaseModel):
    """日历事件"""

    id: int
    title: str
    content_type: str
    scheduled_time: datetime
    end_time: Optional[datetime] = None
    status: str
    priority: int
    color: str  # 前端显示用的颜色


class CalendarData(BaseModel):
    """日历数据"""

    events: list[CalendarEvent]
    month: int
    year: int


# ========== 智能推荐 ==========


class TimeSlot(BaseModel):
    """时间段"""

    hour: int = Field(..., ge=0, le=23)
    score: float = Field(..., ge=0.0, le=100.0)
    reason: str


class SuggestedTime(BaseModel):
    """推荐发布时间"""

    recommended_times: list[TimeSlot]
    content_type: str
    based_on: str  # 基于什么数据（历史数据、用户活跃度等）


# ========== 执行控制 ==========


class ExecuteScheduleRequest(BaseModel):
    """手动执行调度请求"""

    force: bool = False  # 是否强制执行（忽略条件检查）
    reason: Optional[str] = None  # 执行原因


class ExecuteScheduleResponse(BaseModel):
    """执行调度响应"""

    success: bool
    message: str
    schedule_id: int
    execution_time_ms: int


class RollbackRequest(BaseModel):
    """回滚请求"""

    reason: str = Field(..., min_length=1)


class RollbackResponse(BaseModel):
    """回滚响应"""

    success: bool
    message: str
    previous_status: str
    current_status: str
