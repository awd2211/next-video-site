"""
系统告警服务

负责监控系统指标并生成告警，支持多维度告警、去重和生命周期管理
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from loguru import logger

from app.models.system_metrics import SystemAlert, SystemMetrics
from app.utils.cache import get_redis
import json


# 告警阈值配置
class AlertThresholds:
    """告警阈值配置类"""

    # CPU 告警阈值
    CPU_WARNING = 70.0  # CPU使用率超过70%触发警告
    CPU_CRITICAL = 90.0  # CPU使用率超过90%触发严重告警

    # 内存告警阈值
    MEMORY_WARNING = 80.0  # 内存使用率超过80%触发警告
    MEMORY_CRITICAL = 95.0  # 内存使用率超过95%触发严重告警

    # 磁盘告警阈值
    DISK_WARNING = 80.0  # 磁盘使用率超过80%触发警告
    DISK_CRITICAL = 95.0  # 磁盘使用率超过95%触发严重告警

    # 数据库连接池告警阈值
    DB_POOL_WARNING = 70.0  # 连接池使用率超过70%触发警告
    DB_POOL_CRITICAL = 90.0  # 连接池使用率超过90%触发严重告警
    DB_RESPONSE_TIME_WARNING = 100.0  # 响应时间超过100ms触发警告
    DB_RESPONSE_TIME_CRITICAL = 500.0  # 响应时间超过500ms触发严重告警

    # Redis 告警阈值
    REDIS_MEMORY_WARNING = 80.0  # Redis内存使用率超过80%触发警告
    REDIS_MEMORY_CRITICAL = 95.0  # Redis内存使用率超过95%触发严重告警
    REDIS_RESPONSE_TIME_WARNING = 50.0  # 响应时间超过50ms触发警告
    REDIS_RESPONSE_TIME_CRITICAL = 200.0  # 响应时间超过200ms触发严重告警

    # 存储告警阈值
    STORAGE_WARNING = 80.0  # 存储使用率超过80%触发警告
    STORAGE_CRITICAL = 95.0  # 存储使用率超过95%触发严重告警
    STORAGE_RESPONSE_TIME_WARNING = 200.0  # 响应时间超过200ms触发警告
    STORAGE_RESPONSE_TIME_CRITICAL = 1000.0  # 响应时间超过1000ms触发严重告警

    # Celery 告警阈值
    CELERY_WORKER_MIN = 1  # Celery Worker最小数量
    CELERY_TASK_BACKLOG_WARNING = 100  # 任务积压超过100触发警告
    CELERY_TASK_BACKLOG_CRITICAL = 500  # 任务积压超过500触发严重告警


class AlertService:
    """告警服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.thresholds = AlertThresholds()

    async def check_and_create_alerts(
        self,
        metrics: Dict[str, Any]
    ) -> List[SystemAlert]:
        """
        检查指标并创建告警

        Args:
            metrics: 系统指标数据

        Returns:
            创建的告警列表
        """
        alerts = []

        # 检查 CPU
        cpu_alerts = await self._check_cpu_alerts(metrics.get("system_resources", {}).get("cpu", {}))
        alerts.extend(cpu_alerts)

        # 检查内存
        memory_alerts = await self._check_memory_alerts(metrics.get("system_resources", {}).get("memory", {}))
        alerts.extend(memory_alerts)

        # 检查磁盘
        disk_alerts = await self._check_disk_alerts(metrics.get("system_resources", {}).get("disk", {}))
        alerts.extend(disk_alerts)

        # 检查数据库
        db_alerts = await self._check_database_alerts(metrics.get("services", {}).get("database", {}))
        alerts.extend(db_alerts)

        # 检查 Redis
        redis_alerts = await self._check_redis_alerts(metrics.get("services", {}).get("redis", {}))
        alerts.extend(redis_alerts)

        # 检查存储
        storage_alerts = await self._check_storage_alerts(metrics.get("services", {}).get("storage", {}))
        alerts.extend(storage_alerts)

        # 检查 Celery
        celery_alerts = await self._check_celery_alerts(metrics.get("services", {}).get("celery", {}))
        alerts.extend(celery_alerts)

        return alerts

    async def _check_cpu_alerts(self, cpu_metrics: Dict[str, Any]) -> List[SystemAlert]:
        """检查 CPU 告警"""
        alerts = []
        usage = cpu_metrics.get("usage_percent", 0)

        if usage >= self.thresholds.CPU_CRITICAL:
            alert = await self._create_or_update_alert(
                alert_type="cpu",
                severity="critical",
                title="CPU使用率严重告警",
                message=f"CPU使用率达到 {usage}%，已超过严重告警阈值 {self.thresholds.CPU_CRITICAL}%",
                metric_name="cpu_usage_percent",
                metric_value=usage,
                threshold_value=self.thresholds.CPU_CRITICAL,
                context=cpu_metrics
            )
            if alert:
                alerts.append(alert)
        elif usage >= self.thresholds.CPU_WARNING:
            alert = await self._create_or_update_alert(
                alert_type="cpu",
                severity="warning",
                title="CPU使用率告警",
                message=f"CPU使用率达到 {usage}%，已超过告警阈值 {self.thresholds.CPU_WARNING}%",
                metric_name="cpu_usage_percent",
                metric_value=usage,
                threshold_value=self.thresholds.CPU_WARNING,
                context=cpu_metrics
            )
            if alert:
                alerts.append(alert)
        else:
            # 检查是否需要解决现有告警
            await self._resolve_alerts("cpu", "cpu_usage_percent")

        return alerts

    async def _check_memory_alerts(self, memory_metrics: Dict[str, Any]) -> List[SystemAlert]:
        """检查内存告警"""
        alerts = []
        usage = memory_metrics.get("usage_percent", 0)

        if usage >= self.thresholds.MEMORY_CRITICAL:
            alert = await self._create_or_update_alert(
                alert_type="memory",
                severity="critical",
                title="内存使用率严重告警",
                message=f"内存使用率达到 {usage}%，已超过严重告警阈值 {self.thresholds.MEMORY_CRITICAL}%",
                metric_name="memory_usage_percent",
                metric_value=usage,
                threshold_value=self.thresholds.MEMORY_CRITICAL,
                context=memory_metrics
            )
            if alert:
                alerts.append(alert)
        elif usage >= self.thresholds.MEMORY_WARNING:
            alert = await self._create_or_update_alert(
                alert_type="memory",
                severity="warning",
                title="内存使用率告警",
                message=f"内存使用率达到 {usage}%，已超过告警阈值 {self.thresholds.MEMORY_WARNING}%",
                metric_name="memory_usage_percent",
                metric_value=usage,
                threshold_value=self.thresholds.MEMORY_WARNING,
                context=memory_metrics
            )
            if alert:
                alerts.append(alert)
        else:
            await self._resolve_alerts("memory", "memory_usage_percent")

        return alerts

    async def _check_disk_alerts(self, disk_metrics: Dict[str, Any]) -> List[SystemAlert]:
        """检查磁盘告警"""
        alerts = []
        usage = disk_metrics.get("usage_percent", 0)

        if usage >= self.thresholds.DISK_CRITICAL:
            alert = await self._create_or_update_alert(
                alert_type="disk",
                severity="critical",
                title="磁盘使用率严重告警",
                message=f"磁盘使用率达到 {usage}%，已超过严重告警阈值 {self.thresholds.DISK_CRITICAL}%",
                metric_name="disk_usage_percent",
                metric_value=usage,
                threshold_value=self.thresholds.DISK_CRITICAL,
                context=disk_metrics
            )
            if alert:
                alerts.append(alert)
        elif usage >= self.thresholds.DISK_WARNING:
            alert = await self._create_or_update_alert(
                alert_type="disk",
                severity="warning",
                title="磁盘使用率告警",
                message=f"磁盘使用率达到 {usage}%，已超过告警阈值 {self.thresholds.DISK_WARNING}%",
                metric_name="disk_usage_percent",
                metric_value=usage,
                threshold_value=self.thresholds.DISK_WARNING,
                context=disk_metrics
            )
            if alert:
                alerts.append(alert)
        else:
            await self._resolve_alerts("disk", "disk_usage_percent")

        return alerts

    async def _check_database_alerts(self, db_metrics: Dict[str, Any]) -> List[SystemAlert]:
        """检查数据库告警"""
        alerts = []

        # 检查连接池使用率
        pool_utilization = db_metrics.get("utilization_percent", 0)
        if pool_utilization >= self.thresholds.DB_POOL_CRITICAL:
            alert = await self._create_or_update_alert(
                alert_type="database",
                severity="critical",
                title="数据库连接池使用率严重告警",
                message=f"数据库连接池使用率达到 {pool_utilization}%，已超过严重告警阈值 {self.thresholds.DB_POOL_CRITICAL}%",
                metric_name="db_pool_utilization",
                metric_value=pool_utilization,
                threshold_value=self.thresholds.DB_POOL_CRITICAL,
                context=db_metrics
            )
            if alert:
                alerts.append(alert)
        elif pool_utilization >= self.thresholds.DB_POOL_WARNING:
            alert = await self._create_or_update_alert(
                alert_type="database",
                severity="warning",
                title="数据库连接池使用率告警",
                message=f"数据库连接池使用率达到 {pool_utilization}%，已超过告警阈值 {self.thresholds.DB_POOL_WARNING}%",
                metric_name="db_pool_utilization",
                metric_value=pool_utilization,
                threshold_value=self.thresholds.DB_POOL_WARNING,
                context=db_metrics
            )
            if alert:
                alerts.append(alert)
        else:
            await self._resolve_alerts("database", "db_pool_utilization")

        # 检查响应时间
        response_time = db_metrics.get("response_time_ms", 0)
        if response_time >= self.thresholds.DB_RESPONSE_TIME_CRITICAL:
            alert = await self._create_or_update_alert(
                alert_type="database",
                severity="critical",
                title="数据库响应时间严重告警",
                message=f"数据库响应时间达到 {response_time}ms，已超过严重告警阈值 {self.thresholds.DB_RESPONSE_TIME_CRITICAL}ms",
                metric_name="db_response_time_ms",
                metric_value=response_time,
                threshold_value=self.thresholds.DB_RESPONSE_TIME_CRITICAL,
                context=db_metrics
            )
            if alert:
                alerts.append(alert)
        elif response_time >= self.thresholds.DB_RESPONSE_TIME_WARNING:
            alert = await self._create_or_update_alert(
                alert_type="database",
                severity="warning",
                title="数据库响应时间告警",
                message=f"数据库响应时间达到 {response_time}ms，已超过告警阈值 {self.thresholds.DB_RESPONSE_TIME_WARNING}ms",
                metric_name="db_response_time_ms",
                metric_value=response_time,
                threshold_value=self.thresholds.DB_RESPONSE_TIME_WARNING,
                context=db_metrics
            )
            if alert:
                alerts.append(alert)
        else:
            await self._resolve_alerts("database", "db_response_time_ms")

        return alerts

    async def _check_redis_alerts(self, redis_metrics: Dict[str, Any]) -> List[SystemAlert]:
        """检查 Redis 告警"""
        alerts = []

        # 检查内存使用率
        memory_utilization = redis_metrics.get("memory_utilization_percent")
        if memory_utilization is not None:
            if memory_utilization >= self.thresholds.REDIS_MEMORY_CRITICAL:
                alert = await self._create_or_update_alert(
                    alert_type="redis",
                    severity="critical",
                    title="Redis内存使用率严重告警",
                    message=f"Redis内存使用率达到 {memory_utilization}%，已超过严重告警阈值 {self.thresholds.REDIS_MEMORY_CRITICAL}%",
                    metric_name="redis_memory_utilization",
                    metric_value=memory_utilization,
                    threshold_value=self.thresholds.REDIS_MEMORY_CRITICAL,
                    context=redis_metrics
                )
                if alert:
                    alerts.append(alert)
            elif memory_utilization >= self.thresholds.REDIS_MEMORY_WARNING:
                alert = await self._create_or_update_alert(
                    alert_type="redis",
                    severity="warning",
                    title="Redis内存使用率告警",
                    message=f"Redis内存使用率达到 {memory_utilization}%，已超过告警阈值 {self.thresholds.REDIS_MEMORY_WARNING}%",
                    metric_name="redis_memory_utilization",
                    metric_value=memory_utilization,
                    threshold_value=self.thresholds.REDIS_MEMORY_WARNING,
                    context=redis_metrics
                )
                if alert:
                    alerts.append(alert)
            else:
                await self._resolve_alerts("redis", "redis_memory_utilization")

        # 检查响应时间
        response_time = redis_metrics.get("response_time_ms", 0)
        if response_time >= self.thresholds.REDIS_RESPONSE_TIME_CRITICAL:
            alert = await self._create_or_update_alert(
                alert_type="redis",
                severity="critical",
                title="Redis响应时间严重告警",
                message=f"Redis响应时间达到 {response_time}ms，已超过严重告警阈值 {self.thresholds.REDIS_RESPONSE_TIME_CRITICAL}ms",
                metric_name="redis_response_time_ms",
                metric_value=response_time,
                threshold_value=self.thresholds.REDIS_RESPONSE_TIME_CRITICAL,
                context=redis_metrics
            )
            if alert:
                alerts.append(alert)
        elif response_time >= self.thresholds.REDIS_RESPONSE_TIME_WARNING:
            alert = await self._create_or_update_alert(
                alert_type="redis",
                severity="warning",
                title="Redis响应时间告警",
                message=f"Redis响应时间达到 {response_time}ms，已超过告警阈值 {self.thresholds.REDIS_RESPONSE_TIME_WARNING}ms",
                metric_name="redis_response_time_ms",
                metric_value=response_time,
                threshold_value=self.thresholds.REDIS_RESPONSE_TIME_WARNING,
                context=redis_metrics
            )
            if alert:
                alerts.append(alert)
        else:
            await self._resolve_alerts("redis", "redis_response_time_ms")

        return alerts

    async def _check_storage_alerts(self, storage_metrics: Dict[str, Any]) -> List[SystemAlert]:
        """检查存储告警"""
        alerts = []

        # 检查存储使用率
        utilization = storage_metrics.get("utilization_percent")
        if utilization is not None:
            if utilization >= self.thresholds.STORAGE_CRITICAL:
                alert = await self._create_or_update_alert(
                    alert_type="storage",
                    severity="critical",
                    title="存储空间严重不足",
                    message=f"存储使用率达到 {utilization}%，已超过严重告警阈值 {self.thresholds.STORAGE_CRITICAL}%",
                    metric_name="storage_utilization",
                    metric_value=utilization,
                    threshold_value=self.thresholds.STORAGE_CRITICAL,
                    context=storage_metrics
                )
                if alert:
                    alerts.append(alert)
            elif utilization >= self.thresholds.STORAGE_WARNING:
                alert = await self._create_or_update_alert(
                    alert_type="storage",
                    severity="warning",
                    title="存储空间不足",
                    message=f"存储使用率达到 {utilization}%，已超过告警阈值 {self.thresholds.STORAGE_WARNING}%",
                    metric_name="storage_utilization",
                    metric_value=utilization,
                    threshold_value=self.thresholds.STORAGE_WARNING,
                    context=storage_metrics
                )
                if alert:
                    alerts.append(alert)
            else:
                await self._resolve_alerts("storage", "storage_utilization")

        # 检查响应时间
        response_time = storage_metrics.get("response_time_ms", 0)

        if response_time >= self.thresholds.STORAGE_RESPONSE_TIME_CRITICAL:
            alert = await self._create_or_update_alert(
                alert_type="storage",
                severity="critical",
                title="存储响应时间严重告警",
                message=f"存储响应时间达到 {response_time}ms，已超过严重告警阈值 {self.thresholds.STORAGE_RESPONSE_TIME_CRITICAL}ms",
                metric_name="storage_response_time_ms",
                metric_value=response_time,
                threshold_value=self.thresholds.STORAGE_RESPONSE_TIME_CRITICAL,
                context=storage_metrics
            )
            if alert:
                alerts.append(alert)
        elif response_time >= self.thresholds.STORAGE_RESPONSE_TIME_WARNING:
            alert = await self._create_or_update_alert(
                alert_type="storage",
                severity="warning",
                title="存储响应时间告警",
                message=f"存储响应时间达到 {response_time}ms，已超过告警阈值 {self.thresholds.STORAGE_RESPONSE_TIME_WARNING}ms",
                metric_name="storage_response_time_ms",
                metric_value=response_time,
                threshold_value=self.thresholds.STORAGE_RESPONSE_TIME_WARNING,
                context=storage_metrics
            )
            if alert:
                alerts.append(alert)
        else:
            await self._resolve_alerts("storage", "storage_response_time_ms")

        # 检查存储服务状态
        status = storage_metrics.get("status")
        if status == "unhealthy":
            alert = await self._create_or_update_alert(
                alert_type="storage",
                severity="critical",
                title="存储服务不可用",
                message=f"存储服务状态异常: {storage_metrics.get('message', '未知错误')}",
                metric_name="storage_status",
                metric_value=0,
                threshold_value=1,
                context=storage_metrics
            )
            if alert:
                alerts.append(alert)
        else:
            await self._resolve_alerts("storage", "storage_status")

        return alerts

    async def _check_celery_alerts(self, celery_metrics: Dict[str, Any]) -> List[SystemAlert]:
        """检查 Celery 告警"""
        alerts = []

        # 检查 Worker 数量
        workers_count = celery_metrics.get("workers_count", 0)
        if workers_count < self.thresholds.CELERY_WORKER_MIN:
            alert = await self._create_or_update_alert(
                alert_type="celery",
                severity="critical",
                title="Celery Worker数量不足",
                message=f"Celery Worker数量为 {workers_count}，低于最小要求 {self.thresholds.CELERY_WORKER_MIN}",
                metric_name="celery_workers_count",
                metric_value=workers_count,
                threshold_value=self.thresholds.CELERY_WORKER_MIN,
                context=celery_metrics
            )
            if alert:
                alerts.append(alert)
        else:
            await self._resolve_alerts("celery", "celery_workers_count")

        # 检查任务积压
        active_tasks = celery_metrics.get("active_tasks", 0)
        if active_tasks >= self.thresholds.CELERY_TASK_BACKLOG_CRITICAL:
            alert = await self._create_or_update_alert(
                alert_type="celery",
                severity="critical",
                title="Celery任务积压严重",
                message=f"Celery活跃任务数达到 {active_tasks}，已超过严重告警阈值 {self.thresholds.CELERY_TASK_BACKLOG_CRITICAL}",
                metric_name="celery_active_tasks",
                metric_value=active_tasks,
                threshold_value=self.thresholds.CELERY_TASK_BACKLOG_CRITICAL,
                context=celery_metrics
            )
            if alert:
                alerts.append(alert)
        elif active_tasks >= self.thresholds.CELERY_TASK_BACKLOG_WARNING:
            alert = await self._create_or_update_alert(
                alert_type="celery",
                severity="warning",
                title="Celery任务积压告警",
                message=f"Celery活跃任务数达到 {active_tasks}，已超过告警阈值 {self.thresholds.CELERY_TASK_BACKLOG_WARNING}",
                metric_name="celery_active_tasks",
                metric_value=active_tasks,
                threshold_value=self.thresholds.CELERY_TASK_BACKLOG_WARNING,
                context=celery_metrics
            )
            if alert:
                alerts.append(alert)
        else:
            await self._resolve_alerts("celery", "celery_active_tasks")

        # 检查 Celery 服务状态
        status = celery_metrics.get("status")
        if status == "unhealthy":
            alert = await self._create_or_update_alert(
                alert_type="celery",
                severity="critical",
                title="Celery服务不可用",
                message=f"Celery服务状态异常: {celery_metrics.get('message', '未知错误')}",
                metric_name="celery_status",
                metric_value=0,
                threshold_value=1,
                context=celery_metrics
            )
            if alert:
                alerts.append(alert)
        else:
            await self._resolve_alerts("celery", "celery_status")

        return alerts

    async def _create_or_update_alert(
        self,
        alert_type: str,
        severity: str,
        title: str,
        message: str,
        metric_name: str,
        metric_value: float,
        threshold_value: float,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[SystemAlert]:
        """
        创建或更新告警（实现去重逻辑）

        如果相同类型和指标的告警已存在且处于活跃状态，则更新它
        否则创建新告警
        """
        try:
            # 查找最近的活跃告警（最近1小时内的）
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)

            stmt = select(SystemAlert).where(
                and_(
                    SystemAlert.alert_type == alert_type,
                    SystemAlert.metric_name == metric_name,
                    SystemAlert.status == "active",
                    SystemAlert.triggered_at >= one_hour_ago
                )
            ).order_by(SystemAlert.triggered_at.desc())

            result = await self.db.execute(stmt)
            existing_alert = result.scalar_one_or_none()

            if existing_alert:
                # 更新现有告警
                existing_alert.severity = severity
                existing_alert.message = message
                existing_alert.metric_value = metric_value
                existing_alert.threshold_value = threshold_value
                existing_alert.context = context
                existing_alert.updated_at = datetime.utcnow()

                await self.db.commit()
                await self.db.refresh(existing_alert)

                logger.debug(f"Updated existing alert: {alert_type}/{metric_name}")
                return None  # 返回 None 表示这是更新而非新告警
            else:
                # 创建新告警
                new_alert = SystemAlert(
                    alert_type=alert_type,
                    severity=severity,
                    title=title,
                    message=message,
                    metric_name=metric_name,
                    metric_value=metric_value,
                    threshold_value=threshold_value,
                    status="active",
                    context=context,
                    notification_sent=False
                )

                self.db.add(new_alert)
                await self.db.commit()
                await self.db.refresh(new_alert)

                logger.info(f"Created new alert: {alert_type}/{metric_name} - {severity}")
                return new_alert

        except Exception as e:
            logger.error(f"Failed to create/update alert: {e}")
            await self.db.rollback()
            return None

    async def _resolve_alerts(
        self,
        alert_type: str,
        metric_name: str
    ):
        """
        解决指定类型和指标的告警

        将所有活跃的匹配告警标记为已解决
        """
        try:
            stmt = select(SystemAlert).where(
                and_(
                    SystemAlert.alert_type == alert_type,
                    SystemAlert.metric_name == metric_name,
                    SystemAlert.status == "active"
                )
            )

            result = await self.db.execute(stmt)
            active_alerts = result.scalars().all()

            for alert in active_alerts:
                alert.status = "resolved"
                alert.resolved_at = datetime.utcnow()
                alert.updated_at = datetime.utcnow()

            if active_alerts:
                await self.db.commit()
                logger.info(f"Resolved {len(active_alerts)} alerts for {alert_type}/{metric_name}")

        except Exception as e:
            logger.error(f"Failed to resolve alerts: {e}")
            await self.db.rollback()

    async def get_active_alerts(
        self,
        alert_type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[SystemAlert]:
        """
        获取活跃告警列表

        Args:
            alert_type: 告警类型过滤
            severity: 严重程度过滤
            limit: 返回数量限制

        Returns:
            活跃告警列表
        """
        try:
            conditions = [SystemAlert.status == "active"]

            if alert_type:
                conditions.append(SystemAlert.alert_type == alert_type)

            if severity:
                conditions.append(SystemAlert.severity == severity)

            stmt = select(SystemAlert).where(
                and_(*conditions)
            ).order_by(
                SystemAlert.severity.desc(),
                SystemAlert.triggered_at.desc()
            ).limit(limit)

            result = await self.db.execute(stmt)
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []

    async def acknowledge_alert(
        self,
        alert_id: int,
        admin_user_id: int,
        notes: Optional[str] = None
    ) -> Optional[SystemAlert]:
        """
        确认告警

        Args:
            alert_id: 告警ID
            admin_user_id: 确认人ID
            notes: 处理备注

        Returns:
            更新后的告警对象
        """
        try:
            stmt = select(SystemAlert).where(SystemAlert.id == alert_id)
            result = await self.db.execute(stmt)
            alert = result.scalar_one_or_none()

            if not alert:
                return None

            alert.acknowledged_by = admin_user_id
            alert.acknowledged_at = datetime.utcnow()
            alert.notes = notes
            alert.updated_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(alert)

            logger.info(f"Alert {alert_id} acknowledged by admin {admin_user_id}")
            return alert

        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
            await self.db.rollback()
            return None

    async def get_alert_statistics(self) -> Dict[str, Any]:
        """
        获取告警统计信息

        Returns:
            告警统计数据
        """
        try:
            from sqlalchemy import func

            # 获取活跃告警数量
            active_count_stmt = select(func.count(SystemAlert.id)).where(
                SystemAlert.status == "active"
            )
            active_count = await self.db.scalar(active_count_stmt)

            # 获取严重告警数量
            critical_count_stmt = select(func.count(SystemAlert.id)).where(
                and_(
                    SystemAlert.status == "active",
                    SystemAlert.severity == "critical"
                )
            )
            critical_count = await self.db.scalar(critical_count_stmt)

            # 获取警告数量
            warning_count_stmt = select(func.count(SystemAlert.id)).where(
                and_(
                    SystemAlert.status == "active",
                    SystemAlert.severity == "warning"
                )
            )
            warning_count = await self.db.scalar(warning_count_stmt)

            # 获取最近24小时已解决的告警数量
            yesterday = datetime.utcnow() - timedelta(days=1)
            resolved_24h_stmt = select(func.count(SystemAlert.id)).where(
                and_(
                    SystemAlert.status == "resolved",
                    SystemAlert.resolved_at >= yesterday
                )
            )
            resolved_24h = await self.db.scalar(resolved_24h_stmt)

            return {
                "active_total": active_count or 0,
                "critical": critical_count or 0,
                "warning": warning_count or 0,
                "resolved_24h": resolved_24h or 0
            }

        except Exception as e:
            logger.error(f"Failed to get alert statistics: {e}")
            return {
                "active_total": 0,
                "critical": 0,
                "warning": 0,
                "resolved_24h": 0
            }


async def save_metrics_to_database(
    db: AsyncSession,
    metrics: Dict[str, Any]
) -> Optional[SystemMetrics]:
    """
    保存系统指标到数据库

    Args:
        db: 数据库会话
        metrics: 系统指标数据

    Returns:
        创建的 SystemMetrics 对象
    """
    try:
        system_resources = metrics.get("system_resources", {})
        services = metrics.get("services", {})

        cpu = system_resources.get("cpu", {})
        memory = system_resources.get("memory", {})
        disk = system_resources.get("disk", {})
        network = system_resources.get("network", {})
        processes = system_resources.get("processes", {})

        database = services.get("database", {})
        redis = services.get("redis", {})
        storage = services.get("storage", {})
        celery = services.get("celery", {})

        metric_record = SystemMetrics(
            # CPU 指标
            cpu_usage_percent=cpu.get("usage_percent"),
            cpu_cores=cpu.get("cores"),

            # 内存指标
            memory_usage_percent=memory.get("usage_percent"),
            memory_used_gb=memory.get("used_gb"),
            memory_total_gb=memory.get("total_gb"),
            memory_available_gb=memory.get("available_gb"),

            # 磁盘指标
            disk_usage_percent=disk.get("usage_percent"),
            disk_used_gb=disk.get("used_gb"),
            disk_total_gb=disk.get("total_gb"),
            disk_free_gb=disk.get("free_gb"),

            # 网络指标
            network_bytes_sent_gb=network.get("bytes_sent_gb"),
            network_bytes_recv_gb=network.get("bytes_recv_gb"),
            network_errors=network.get("errors_in", 0) + network.get("errors_out", 0),

            # 数据库指标
            db_response_time_ms=database.get("response_time_ms"),
            db_pool_size=database.get("pool_size"),
            db_pool_checked_out=database.get("checked_out"),
            db_pool_utilization=database.get("utilization_percent"),

            # Redis 指标
            redis_response_time_ms=redis.get("response_time_ms"),
            redis_used_memory_mb=redis.get("used_memory_mb"),
            redis_memory_utilization=redis.get("memory_utilization_percent"),
            redis_keys_count=redis.get("keys_count"),

            # 存储指标
            storage_response_time_ms=storage.get("response_time_ms"),
            storage_used_gb=storage.get("used_gb"),
            storage_total_gb=storage.get("total_gb"),
            storage_utilization=storage.get("utilization_percent"),

            # 服务状态
            overall_status=metrics.get("overall_status"),
            database_status=database.get("status"),
            redis_status=redis.get("status"),
            storage_status=storage.get("status"),

            # 进程信息
            process_count=processes.get("count"),

            # Celery 指标
            celery_active_tasks=celery.get("active_tasks"),
            celery_workers_count=celery.get("workers_count"),

            # 额外元数据
            extra_metadata={
                "celery_reserved_tasks": celery.get("reserved_tasks"),
                "network_packets": {
                    "sent": network.get("packets_sent"),
                    "recv": network.get("packets_recv")
                },
                "network_drops": {
                    "in": network.get("drops_in"),
                    "out": network.get("drops_out")
                }
            }
        )

        db.add(metric_record)
        await db.commit()
        await db.refresh(metric_record)

        logger.debug(f"Saved metrics to database: {metric_record.id}")
        return metric_record

    except Exception as e:
        logger.error(f"Failed to save metrics to database: {e}")
        await db.rollback()
        return None
