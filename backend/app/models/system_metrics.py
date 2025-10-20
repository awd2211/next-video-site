"""
系统监控指标数据模型

用于持久化系统健康监控数据，支持历史查询和趋势分析
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Float, Integer, JSON, String, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class SystemMetrics(Base):
    """
    系统指标历史记录表

    存储系统健康监控的时间序列数据
    """

    __tablename__ = "system_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 时间戳
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        server_default=func.now(),
        comment="指标采集时间"
    )

    # CPU指标
    cpu_usage_percent: Mapped[Optional[float]] = mapped_column(Float, comment="CPU使用率(%)")
    cpu_cores: Mapped[Optional[int]] = mapped_column(Integer, comment="CPU核心数")

    # 内存指标
    memory_usage_percent: Mapped[Optional[float]] = mapped_column(Float, comment="内存使用率(%)")
    memory_used_gb: Mapped[Optional[float]] = mapped_column(Float, comment="已用内存(GB)")
    memory_total_gb: Mapped[Optional[float]] = mapped_column(Float, comment="总内存(GB)")
    memory_available_gb: Mapped[Optional[float]] = mapped_column(Float, comment="可用内存(GB)")

    # 磁盘指标
    disk_usage_percent: Mapped[Optional[float]] = mapped_column(Float, comment="磁盘使用率(%)")
    disk_used_gb: Mapped[Optional[float]] = mapped_column(Float, comment="已用磁盘(GB)")
    disk_total_gb: Mapped[Optional[float]] = mapped_column(Float, comment="总磁盘(GB)")
    disk_free_gb: Mapped[Optional[float]] = mapped_column(Float, comment="可用磁盘(GB)")

    # 网络指标
    network_bytes_sent_gb: Mapped[Optional[float]] = mapped_column(Float, comment="发送流量(GB)")
    network_bytes_recv_gb: Mapped[Optional[float]] = mapped_column(Float, comment="接收流量(GB)")
    network_errors: Mapped[Optional[int]] = mapped_column(Integer, comment="网络错误数")

    # 数据库指标
    db_response_time_ms: Mapped[Optional[float]] = mapped_column(Float, comment="数据库响应时间(ms)")
    db_pool_size: Mapped[Optional[int]] = mapped_column(Integer, comment="数据库连接池大小")
    db_pool_checked_out: Mapped[Optional[int]] = mapped_column(Integer, comment="已检出连接数")
    db_pool_utilization: Mapped[Optional[float]] = mapped_column(Float, comment="连接池使用率(%)")

    # Redis指标
    redis_response_time_ms: Mapped[Optional[float]] = mapped_column(Float, comment="Redis响应时间(ms)")
    redis_used_memory_mb: Mapped[Optional[float]] = mapped_column(Float, comment="Redis已用内存(MB)")
    redis_memory_utilization: Mapped[Optional[float]] = mapped_column(Float, comment="Redis内存使用率(%)")
    redis_keys_count: Mapped[Optional[int]] = mapped_column(Integer, comment="Redis键数量")

    # 存储指标
    storage_response_time_ms: Mapped[Optional[float]] = mapped_column(Float, comment="存储响应时间(ms)")
    storage_used_gb: Mapped[Optional[float]] = mapped_column(Float, comment="存储已用空间(GB)")
    storage_total_gb: Mapped[Optional[float]] = mapped_column(Float, comment="存储总空间(GB)")
    storage_utilization: Mapped[Optional[float]] = mapped_column(Float, comment="存储使用率(%)")

    # 服务状态
    overall_status: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="总体状态(healthy/degraded/unhealthy)"
    )
    database_status: Mapped[Optional[str]] = mapped_column(String(20), comment="数据库状态")
    redis_status: Mapped[Optional[str]] = mapped_column(String(20), comment="Redis状态")
    storage_status: Mapped[Optional[str]] = mapped_column(String(20), comment="存储状态")

    # 进程和任务
    process_count: Mapped[Optional[int]] = mapped_column(Integer, comment="系统进程数")
    celery_active_tasks: Mapped[Optional[int]] = mapped_column(Integer, comment="Celery活跃任务数")
    celery_workers_count: Mapped[Optional[int]] = mapped_column(Integer, comment="Celery Worker数量")

    # 额外元数据（JSON格式）
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON, comment="额外元数据")

    # 创建时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="记录创建时间"
    )

    # 索引优化：按时间戳查询
    __table_args__ = (
        Index('idx_system_metrics_timestamp', 'timestamp'),
        Index('idx_system_metrics_status', 'overall_status'),
        Index('idx_system_metrics_created_at', 'created_at'),
    )


class SystemAlert(Base):
    """
    系统告警记录表

    记录触发的告警，支持告警历史查询和统计
    """

    __tablename__ = "system_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 告警基本信息
    alert_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="告警类型(cpu/memory/disk/database/redis/storage/celery)"
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="严重程度(info/warning/critical)"
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="告警标题")
    message: Mapped[str] = mapped_column(String(1000), nullable=False, comment="告警消息")

    # 指标详情
    metric_name: Mapped[Optional[str]] = mapped_column(String(100), comment="指标名称")
    metric_value: Mapped[Optional[float]] = mapped_column(Float, comment="指标当前值")
    threshold_value: Mapped[Optional[float]] = mapped_column(Float, comment="阈值")

    # 告警状态
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        index=True,
        comment="告警状态(active/resolved/ignored)"
    )

    # 时间信息
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="触发时间"
    )

    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        comment="解决时间"
    )

    # 通知信息
    notification_sent: Mapped[bool] = mapped_column(
        default=False,
        comment="是否已发送通知"
    )

    notification_channels: Mapped[Optional[str]] = mapped_column(
        String(200),
        comment="通知渠道(email,websocket,system)"
    )

    # 处理信息
    acknowledged_by: Mapped[Optional[int]] = mapped_column(Integer, comment="确认人ID")
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        comment="确认时间"
    )

    notes: Mapped[Optional[str]] = mapped_column(String(1000), comment="处理备注")

    # 额外数据
    context: Mapped[Optional[dict]] = mapped_column(JSON, comment="告警上下文数据")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="记录创建时间"
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment="记录更新时间"
    )

    # 索引优化
    __table_args__ = (
        Index('idx_system_alerts_type_severity', 'alert_type', 'severity'),
        Index('idx_system_alerts_status', 'status'),
        Index('idx_system_alerts_triggered_at', 'triggered_at'),
    )


class SystemSLA(Base):
    """
    系统SLA统计表

    记录系统可用性和性能SLA数据
    """

    __tablename__ = "system_sla"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 时间范围
    period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="统计周期开始时间"
    )

    period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="统计周期结束时间"
    )

    period_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="周期类型(hourly/daily/weekly/monthly)"
    )

    # 可用性指标
    uptime_seconds: Mapped[int] = mapped_column(Integer, comment="正常运行时间(秒)")
    downtime_seconds: Mapped[int] = mapped_column(Integer, comment="停机时间(秒)")
    uptime_percentage: Mapped[float] = mapped_column(Float, comment="可用性百分比")

    # API性能指标
    total_requests: Mapped[int] = mapped_column(Integer, default=0, comment="总请求数")
    successful_requests: Mapped[int] = mapped_column(Integer, default=0, comment="成功请求数")
    failed_requests: Mapped[int] = mapped_column(Integer, default=0, comment="失败请求数")
    success_rate: Mapped[Optional[float]] = mapped_column(Float, comment="成功率(%)")

    # 响应时间指标
    avg_response_time_ms: Mapped[Optional[float]] = mapped_column(Float, comment="平均响应时间(ms)")
    p50_response_time_ms: Mapped[Optional[float]] = mapped_column(Float, comment="P50响应时间(ms)")
    p95_response_time_ms: Mapped[Optional[float]] = mapped_column(Float, comment="P95响应时间(ms)")
    p99_response_time_ms: Mapped[Optional[float]] = mapped_column(Float, comment="P99响应时间(ms)")
    max_response_time_ms: Mapped[Optional[float]] = mapped_column(Float, comment="最大响应时间(ms)")

    # 告警统计
    total_alerts: Mapped[int] = mapped_column(Integer, default=0, comment="总告警数")
    critical_alerts: Mapped[int] = mapped_column(Integer, default=0, comment="严重告警数")
    warning_alerts: Mapped[int] = mapped_column(Integer, default=0, comment="警告数")

    # 资源使用统计
    avg_cpu_usage: Mapped[Optional[float]] = mapped_column(Float, comment="平均CPU使用率(%)")
    avg_memory_usage: Mapped[Optional[float]] = mapped_column(Float, comment="平均内存使用率(%)")
    avg_disk_usage: Mapped[Optional[float]] = mapped_column(Float, comment="平均磁盘使用率(%)")

    # 元数据
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON, comment="额外统计数据")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="记录创建时间"
    )

    # 索引优化
    __table_args__ = (
        Index('idx_system_sla_period', 'period_start', 'period_end'),
        Index('idx_system_sla_type', 'period_type'),
    )
