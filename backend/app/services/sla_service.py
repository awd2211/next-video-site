"""
SLA追踪服务

计算和存储系统服务水平协议（SLA）指标，包括可用性、响应时间、成功率等
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from loguru import logger
import statistics

from app.models.system_metrics import SystemMetrics, SystemAlert, SystemSLA


class SLAService:
    """SLA追踪服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_sla(
        self,
        period_start: datetime,
        period_end: datetime,
        period_type: str = "hourly"
    ) -> Optional[SystemSLA]:
        """
        计算指定时间段的SLA指标

        Args:
            period_start: 统计周期开始时间
            period_end: 统计周期结束时间
            period_type: 周期类型 (hourly/daily/weekly/monthly)

        Returns:
            SystemSLA对象
        """
        try:
            # 查询该时间段内的所有指标记录
            stmt = select(SystemMetrics).where(
                and_(
                    SystemMetrics.timestamp >= period_start,
                    SystemMetrics.timestamp < period_end
                )
            ).order_by(SystemMetrics.timestamp)

            result = await self.db.execute(stmt)
            metrics = result.scalars().all()

            if not metrics:
                logger.warning(f"No metrics found for period {period_start} to {period_end}")
                return None

            # 计算可用性指标
            uptime_stats = self._calculate_uptime(metrics, period_start, period_end)

            # 计算响应时间指标
            response_time_stats = self._calculate_response_times(metrics)

            # 查询该时间段内的告警统计
            alert_stats = await self._calculate_alert_stats(period_start, period_end)

            # 计算资源使用统计
            resource_stats = self._calculate_resource_usage(metrics)

            # 创建SLA记录
            sla_record = SystemSLA(
                period_start=period_start,
                period_end=period_end,
                period_type=period_type,

                # 可用性指标
                uptime_seconds=uptime_stats["uptime_seconds"],
                downtime_seconds=uptime_stats["downtime_seconds"],
                uptime_percentage=uptime_stats["uptime_percentage"],

                # 请求统计（目前暂无请求日志，使用默认值）
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                success_rate=None,

                # 响应时间指标
                avg_response_time_ms=response_time_stats.get("avg_response_time"),
                p50_response_time_ms=response_time_stats.get("p50_response_time"),
                p95_response_time_ms=response_time_stats.get("p95_response_time"),
                p99_response_time_ms=response_time_stats.get("p99_response_time"),
                max_response_time_ms=response_time_stats.get("max_response_time"),

                # 告警统计
                total_alerts=alert_stats["total_alerts"],
                critical_alerts=alert_stats["critical_alerts"],
                warning_alerts=alert_stats["warning_alerts"],

                # 资源使用统计
                avg_cpu_usage=resource_stats.get("avg_cpu_usage"),
                avg_memory_usage=resource_stats.get("avg_memory_usage"),
                avg_disk_usage=resource_stats.get("avg_disk_usage"),

                # 额外元数据
                extra_metadata={
                    "metrics_count": len(metrics),
                    "db_avg_response_time": response_time_stats.get("db_avg_response_time"),
                    "redis_avg_response_time": response_time_stats.get("redis_avg_response_time"),
                    "storage_avg_response_time": response_time_stats.get("storage_avg_response_time"),
                    "avg_db_pool_utilization": resource_stats.get("avg_db_pool_utilization"),
                    "max_db_pool_utilization": resource_stats.get("max_db_pool_utilization"),
                }
            )

            self.db.add(sla_record)
            await self.db.commit()
            await self.db.refresh(sla_record)

            logger.info(f"SLA record created for {period_type} period: {period_start} to {period_end}")
            return sla_record

        except Exception as e:
            logger.error(f"Failed to calculate SLA: {e}")
            await self.db.rollback()
            return None

    def _calculate_uptime(
        self,
        metrics: List[SystemMetrics],
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """
        计算可用性指标

        根据系统状态判断uptime和downtime
        """
        total_seconds = int((period_end - period_start).total_seconds())

        # 统计unhealthy状态的记录数
        unhealthy_count = sum(1 for m in metrics if m.overall_status == "unhealthy")
        healthy_count = len(metrics) - unhealthy_count

        # 假设每个指标代表采集间隔（通常5秒）
        # 如果没有指标，假设系统运行正常
        if len(metrics) == 0:
            return {
                "uptime_seconds": total_seconds,
                "downtime_seconds": 0,
                "uptime_percentage": 100.0
            }

        # 计算平均采集间隔
        if len(metrics) > 1:
            time_span = (metrics[-1].timestamp - metrics[0].timestamp).total_seconds()
            avg_interval = time_span / (len(metrics) - 1) if len(metrics) > 1 else 5
        else:
            avg_interval = 5

        # 估算downtime
        downtime_seconds = int(unhealthy_count * avg_interval)
        uptime_seconds = max(0, total_seconds - downtime_seconds)

        # 计算可用性百分比
        uptime_percentage = (uptime_seconds / total_seconds * 100) if total_seconds > 0 else 100.0

        return {
            "uptime_seconds": uptime_seconds,
            "downtime_seconds": downtime_seconds,
            "uptime_percentage": round(uptime_percentage, 4)
        }

    def _calculate_response_times(self, metrics: List[SystemMetrics]) -> Dict[str, Optional[float]]:
        """
        计算响应时间统计

        从指标中提取各服务的响应时间并计算统计值
        """
        # 收集所有响应时间数据
        db_response_times = [m.db_response_time_ms for m in metrics if m.db_response_time_ms is not None]
        redis_response_times = [m.redis_response_time_ms for m in metrics if m.redis_response_time_ms is not None]
        storage_response_times = [m.storage_response_time_ms for m in metrics if m.storage_response_time_ms is not None]

        # 合并所有响应时间
        all_response_times = db_response_times + redis_response_times + storage_response_times

        if not all_response_times:
            return {
                "avg_response_time": None,
                "p50_response_time": None,
                "p95_response_time": None,
                "p99_response_time": None,
                "max_response_time": None,
                "db_avg_response_time": None,
                "redis_avg_response_time": None,
                "storage_avg_response_time": None,
            }

        # 计算百分位数
        sorted_times = sorted(all_response_times)
        count = len(sorted_times)

        return {
            "avg_response_time": round(statistics.mean(all_response_times), 2),
            "p50_response_time": round(sorted_times[int(count * 0.5)], 2) if count > 0 else None,
            "p95_response_time": round(sorted_times[int(count * 0.95)], 2) if count > 0 else None,
            "p99_response_time": round(sorted_times[int(count * 0.99)], 2) if count > 0 else None,
            "max_response_time": round(max(all_response_times), 2),
            "db_avg_response_time": round(statistics.mean(db_response_times), 2) if db_response_times else None,
            "redis_avg_response_time": round(statistics.mean(redis_response_times), 2) if redis_response_times else None,
            "storage_avg_response_time": round(statistics.mean(storage_response_times), 2) if storage_response_times else None,
        }

    async def _calculate_alert_stats(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, int]:
        """
        计算告警统计

        统计该时间段内触发的告警数量
        """
        try:
            # 统计总告警数
            total_stmt = select(func.count(SystemAlert.id)).where(
                and_(
                    SystemAlert.triggered_at >= period_start,
                    SystemAlert.triggered_at < period_end
                )
            )
            total_alerts = await self.db.scalar(total_stmt)

            # 统计严重告警
            critical_stmt = select(func.count(SystemAlert.id)).where(
                and_(
                    SystemAlert.triggered_at >= period_start,
                    SystemAlert.triggered_at < period_end,
                    SystemAlert.severity == "critical"
                )
            )
            critical_alerts = await self.db.scalar(critical_stmt)

            # 统计警告
            warning_stmt = select(func.count(SystemAlert.id)).where(
                and_(
                    SystemAlert.triggered_at >= period_start,
                    SystemAlert.triggered_at < period_end,
                    SystemAlert.severity == "warning"
                )
            )
            warning_alerts = await self.db.scalar(warning_stmt)

            return {
                "total_alerts": total_alerts or 0,
                "critical_alerts": critical_alerts or 0,
                "warning_alerts": warning_alerts or 0
            }

        except Exception as e:
            logger.error(f"Failed to calculate alert stats: {e}")
            return {
                "total_alerts": 0,
                "critical_alerts": 0,
                "warning_alerts": 0
            }

    def _calculate_resource_usage(self, metrics: List[SystemMetrics]) -> Dict[str, Optional[float]]:
        """
        计算资源使用统计

        计算CPU、内存、磁盘等资源的平均使用率
        """
        cpu_usages = [m.cpu_usage_percent for m in metrics if m.cpu_usage_percent is not None]
        memory_usages = [m.memory_usage_percent for m in metrics if m.memory_usage_percent is not None]
        disk_usages = [m.disk_usage_percent for m in metrics if m.disk_usage_percent is not None]
        db_pool_utilizations = [m.db_pool_utilization for m in metrics if m.db_pool_utilization is not None]

        return {
            "avg_cpu_usage": round(statistics.mean(cpu_usages), 2) if cpu_usages else None,
            "avg_memory_usage": round(statistics.mean(memory_usages), 2) if memory_usages else None,
            "avg_disk_usage": round(statistics.mean(disk_usages), 2) if disk_usages else None,
            "avg_db_pool_utilization": round(statistics.mean(db_pool_utilizations), 2) if db_pool_utilizations else None,
            "max_db_pool_utilization": round(max(db_pool_utilizations), 2) if db_pool_utilizations else None,
        }

    async def get_sla_report(
        self,
        period_type: str = "daily",
        limit: int = 30
    ) -> List[SystemSLA]:
        """
        获取SLA报告

        Args:
            period_type: 周期类型 (hourly/daily/weekly/monthly)
            limit: 返回记录数量

        Returns:
            SLA记录列表
        """
        try:
            stmt = select(SystemSLA).where(
                SystemSLA.period_type == period_type
            ).order_by(
                SystemSLA.period_start.desc()
            ).limit(limit)

            result = await self.db.execute(stmt)
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"Failed to get SLA report: {e}")
            return []

    async def get_sla_summary(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """
        获取SLA汇总统计

        Args:
            period_start: 开始时间
            period_end: 结束时间

        Returns:
            SLA汇总数据
        """
        try:
            stmt = select(SystemSLA).where(
                and_(
                    SystemSLA.period_start >= period_start,
                    SystemSLA.period_end <= period_end
                )
            ).order_by(SystemSLA.period_start)

            result = await self.db.execute(stmt)
            sla_records = result.scalars().all()

            if not sla_records:
                return {
                    "period_start": period_start.isoformat(),
                    "period_end": period_end.isoformat(),
                    "record_count": 0,
                    "avg_uptime_percentage": None,
                    "total_downtime_seconds": 0,
                    "total_alerts": 0,
                    "critical_alerts": 0,
                    "avg_response_time_ms": None,
                }

            # 计算汇总统计
            total_uptime_seconds = sum(r.uptime_seconds for r in sla_records)
            total_downtime_seconds = sum(r.downtime_seconds for r in sla_records)
            total_seconds = total_uptime_seconds + total_downtime_seconds

            avg_uptime_percentage = (total_uptime_seconds / total_seconds * 100) if total_seconds > 0 else 100.0

            response_times = [r.avg_response_time_ms for r in sla_records if r.avg_response_time_ms is not None]
            avg_response_time = statistics.mean(response_times) if response_times else None

            total_alerts = sum(r.total_alerts for r in sla_records)
            critical_alerts = sum(r.critical_alerts for r in sla_records)

            return {
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "record_count": len(sla_records),
                "avg_uptime_percentage": round(avg_uptime_percentage, 4),
                "total_uptime_seconds": total_uptime_seconds,
                "total_downtime_seconds": total_downtime_seconds,
                "total_alerts": total_alerts,
                "critical_alerts": critical_alerts,
                "avg_response_time_ms": round(avg_response_time, 2) if avg_response_time else None,
                "records": [
                    {
                        "period_start": r.period_start.isoformat(),
                        "period_end": r.period_end.isoformat(),
                        "uptime_percentage": r.uptime_percentage,
                        "avg_response_time_ms": r.avg_response_time_ms,
                        "total_alerts": r.total_alerts,
                        "critical_alerts": r.critical_alerts,
                    }
                    for r in sla_records
                ]
            }

        except Exception as e:
            logger.error(f"Failed to get SLA summary: {e}")
            return {
                "error": str(e),
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
            }


async def generate_hourly_sla(db: AsyncSession) -> Optional[SystemSLA]:
    """
    生成上一小时的SLA报告

    Args:
        db: 数据库会话

    Returns:
        SystemSLA对象
    """
    now = datetime.utcnow()
    # 计算上一个整点
    period_end = now.replace(minute=0, second=0, microsecond=0)
    period_start = period_end - timedelta(hours=1)

    sla_service = SLAService(db)
    return await sla_service.calculate_sla(period_start, period_end, "hourly")


async def generate_daily_sla(db: AsyncSession) -> Optional[SystemSLA]:
    """
    生成昨天的SLA报告

    Args:
        db: 数据库会话

    Returns:
        SystemSLA对象
    """
    now = datetime.utcnow()
    # 计算昨天的起止时间
    period_end = now.replace(hour=0, minute=0, second=0, microsecond=0)
    period_start = period_end - timedelta(days=1)

    sla_service = SLAService(db)
    return await sla_service.calculate_sla(period_start, period_end, "daily")


async def generate_weekly_sla(db: AsyncSession) -> Optional[SystemSLA]:
    """
    生成上周的SLA报告

    Args:
        db: 数据库会话

    Returns:
        SystemSLA对象
    """
    now = datetime.utcnow()
    # 计算上周的起止时间（周一到周日）
    days_since_monday = now.weekday()
    period_end = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
    period_start = period_end - timedelta(days=7)

    sla_service = SLAService(db)
    return await sla_service.calculate_sla(period_start, period_end, "weekly")


async def generate_monthly_sla(db: AsyncSession) -> Optional[SystemSLA]:
    """
    生成上月的SLA报告

    Args:
        db: 数据库会话

    Returns:
        SystemSLA对象
    """
    now = datetime.utcnow()
    # 计算上月的起止时间
    period_end = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if period_end.month == 1:
        period_start = period_end.replace(year=period_end.year - 1, month=12)
    else:
        period_start = period_end.replace(month=period_end.month - 1)

    sla_service = SLAService(db)
    return await sla_service.calculate_sla(period_start, period_end, "monthly")
