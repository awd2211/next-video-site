"""
增强版调度任务系统
添加更多智能功能和优化
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List

from celery import Task, group
from loguru import logger
from sqlalchemy import and_, func, or_, select

from app.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models.scheduling import (
    ContentSchedule,
    ScheduleHistory,
    ScheduleStatus,
    ScheduleContentType,
)
from app.services.scheduling_service import SchedulingService
from app.utils.admin_notification_service import AdminNotificationService


# ========== 核心调度任务 ==========


@celery_app.task(
    name="scheduler.execute_due_schedules",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def execute_due_schedules(self):
    """
    执行所有到期的调度任务
    - 每分钟执行一次
    - 支持并发执行
    - 失败自动重试
    """
    import asyncio

    try:
        result = asyncio.run(_execute_due_schedules_async())

        # 如果有失败的任务，记录日志
        if result.get("failed_count", 0) > 0:
            logger.warning(
                f"Some schedules failed to execute: {result['failed_count']}/{result['total']}"
            )

        return result

    except Exception as exc:
        logger.exception(f"Critical error in execute_due_schedules: {exc}")
        # 重试任务
        raise self.retry(exc=exc)


async def _execute_due_schedules_async() -> Dict:
    """异步执行到期任务"""
    async with AsyncSessionLocal() as db:
        try:
            service = SchedulingService(db)

            # 获取所有到期任务（按优先级排序）
            due_schedules = await service.get_due_schedules()

            if not due_schedules:
                return {"executed_count": 0, "failed_count": 0, "total": 0}

            logger.info(f"⏰ Found {len(due_schedules)} due schedules to execute")

            executed_count = 0
            failed_count = 0
            errors = []

            # 按优先级分组执行
            high_priority = [s for s in due_schedules if s.priority >= 80]
            normal_priority = [s for s in due_schedules if 50 <= s.priority < 80]
            low_priority = [s for s in due_schedules if s.priority < 50]

            # 高优先级任务先执行
            for schedule_group, priority_name in [
                (high_priority, "HIGH"),
                (normal_priority, "NORMAL"),
                (low_priority, "LOW"),
            ]:
                if not schedule_group:
                    continue

                logger.info(f"Executing {len(schedule_group)} {priority_name} priority tasks")

                for schedule in schedule_group:
                    try:
                        success, message = await service.execute_schedule(
                            schedule.id, executed_by=None
                        )

                        if success:
                            executed_count += 1
                            logger.info(
                                f"✅ Schedule {schedule.id} executed: "
                                f"{schedule.content_type.value}:{schedule.content_id}"
                            )
                        else:
                            failed_count += 1
                            errors.append({
                                "schedule_id": schedule.id,
                                "content_type": schedule.content_type.value,
                                "content_id": schedule.content_id,
                                "error": message,
                            })
                            logger.error(f"❌ Schedule {schedule.id} failed: {message}")

                    except Exception as e:
                        failed_count += 1
                        errors.append({
                            "schedule_id": schedule.id,
                            "error": str(e),
                        })
                        logger.exception(f"❌ Exception executing schedule {schedule.id}: {e}")

            # 如果有失败的任务，发送通知给管理员
            if failed_count > 0:
                await _notify_execution_failures(db, errors)

            result = {
                "executed_count": executed_count,
                "failed_count": failed_count,
                "total": len(due_schedules),
                "errors": errors if errors else None,
            }

            logger.info(
                f"📊 Execution summary: "
                f"✅ {executed_count} succeeded, ❌ {failed_count} failed"
            )

            return result

        except Exception as e:
            logger.exception(f"Critical error in _execute_due_schedules_async: {e}")
            raise


async def _notify_execution_failures(db, errors: List[Dict]):
    """通知管理员执行失败的任务"""
    try:
        message = f"调度任务执行失败: {len(errors)} 个任务未能成功执行"
        details = "\n".join([
            f"- Schedule #{e.get('schedule_id')}: {e.get('error', 'Unknown error')}"
            for e in errors[:10]  # 只显示前10个错误
        ])

        await AdminNotificationService.notify_system_alert(
            db=db,
            alert_type="schedule_execution_failed",
            severity="high",
            message=message,
            details={"errors": errors[:10], "total_failed": len(errors)},
        )

        logger.info(f"Sent failure notification for {len(errors)} failed schedules")

    except Exception as e:
        logger.exception(f"Failed to send execution failure notification: {e}")


# ========== 智能调度优化 ==========


@celery_app.task(name="scheduler.optimize_schedule_times")
def optimize_schedule_times():
    """
    智能优化调度时间
    - 分析历史数据
    - 避开高峰时段
    - 平衡服务器负载
    """
    import asyncio
    return asyncio.run(_optimize_schedule_times_async())


async def _optimize_schedule_times_async() -> Dict:
    """异步优化调度时间"""
    async with AsyncSessionLocal() as db:
        try:
            # 获取未来24小时的待执行任务
            now = datetime.now(timezone.utc)
            future_24h = now + timedelta(hours=24)

            result = await db.execute(
                select(ContentSchedule)
                .where(
                    and_(
                        ContentSchedule.status == ScheduleStatus.PENDING,
                        ContentSchedule.scheduled_time.between(now, future_24h),
                    )
                )
                .order_by(ContentSchedule.scheduled_time)
            )

            schedules = list(result.scalars().all())

            if len(schedules) < 10:
                return {"message": "Not enough schedules to optimize", "count": len(schedules)}

            # 按小时分组统计
            hourly_counts = {}
            for schedule in schedules:
                hour = schedule.scheduled_time.hour
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1

            # 找出负载最高的小时
            max_load_hour = max(hourly_counts, key=hourly_counts.get)
            max_load = hourly_counts[max_load_hour]

            # 如果某个小时超过10个任务，建议分散
            optimized_count = 0
            if max_load > 10:
                logger.info(
                    f"High load detected at hour {max_load_hour}: {max_load} tasks"
                )

                # TODO: 实现任务重新分配逻辑
                # 这里可以根据业务需求自动调整时间

                optimized_count = 0  # 实际调整的任务数

            return {
                "total_schedules": len(schedules),
                "hourly_distribution": hourly_counts,
                "max_load_hour": max_load_hour,
                "max_load": max_load,
                "optimized_count": optimized_count,
            }

        except Exception as e:
            logger.exception(f"Error in optimize_schedule_times: {e}")
            return {"error": str(e)}


# ========== 冲突检测 ==========


@celery_app.task(name="scheduler.detect_conflicts")
def detect_conflicts():
    """
    检测调度冲突
    - 相同内容重复调度
    - 时间过于接近的调度
    - 资源冲突
    """
    import asyncio
    return asyncio.run(_detect_conflicts_async())


async def _detect_conflicts_async() -> Dict:
    """异步检测冲突"""
    async with AsyncSessionLocal() as db:
        try:
            now = datetime.now(timezone.utc)
            future_7days = now + timedelta(days=7)

            # 获取未来7天的待执行任务
            result = await db.execute(
                select(ContentSchedule)
                .where(
                    and_(
                        ContentSchedule.status == ScheduleStatus.PENDING,
                        ContentSchedule.scheduled_time.between(now, future_7days),
                    )
                )
                .order_by(ContentSchedule.content_type, ContentSchedule.content_id)
            )

            schedules = list(result.scalars().all())

            conflicts = []

            # 检测1: 相同内容的重复调度
            content_map = {}
            for schedule in schedules:
                key = f"{schedule.content_type.value}:{schedule.content_id}"
                if key not in content_map:
                    content_map[key] = []
                content_map[key].append(schedule)

            for key, schedule_list in content_map.items():
                if len(schedule_list) > 1:
                    conflicts.append({
                        "type": "duplicate_content",
                        "content": key,
                        "schedules": [s.id for s in schedule_list],
                        "times": [s.scheduled_time.isoformat() for s in schedule_list],
                    })

            # 检测2: 同一时间（5分钟内）的过多任务
            time_buckets = {}
            for schedule in schedules:
                # 按5分钟分桶
                bucket_time = schedule.scheduled_time.replace(
                    minute=(schedule.scheduled_time.minute // 5) * 5,
                    second=0,
                    microsecond=0
                )
                bucket_key = bucket_time.isoformat()

                if bucket_key not in time_buckets:
                    time_buckets[bucket_key] = []
                time_buckets[bucket_key].append(schedule)

            for bucket_key, schedule_list in time_buckets.items():
                if len(schedule_list) > 5:  # 5分钟内超过5个任务
                    conflicts.append({
                        "type": "high_concurrency",
                        "time_bucket": bucket_key,
                        "count": len(schedule_list),
                        "schedules": [s.id for s in schedule_list],
                    })

            # 如果发现冲突，发送通知
            if conflicts:
                await _notify_conflicts(db, conflicts)

            return {
                "total_checked": len(schedules),
                "conflicts_found": len(conflicts),
                "conflicts": conflicts,
            }

        except Exception as e:
            logger.exception(f"Error in detect_conflicts: {e}")
            return {"error": str(e)}


async def _notify_conflicts(db, conflicts: List[Dict]):
    """通知管理员发现的冲突"""
    try:
        message = f"检测到 {len(conflicts)} 个调度冲突"

        await AdminNotificationService.notify_system_alert(
            db=db,
            alert_type="schedule_conflict",
            severity="medium",
            message=message,
            details={"conflicts": conflicts},
        )

        logger.info(f"Sent conflict notification: {len(conflicts)} conflicts")

    except Exception as e:
        logger.exception(f"Failed to send conflict notification: {e}")


# ========== 每日报告生成 ==========


@celery_app.task(name="scheduler.generate_daily_report")
def generate_daily_report():
    """
    生成每日调度报告
    - 昨日执行统计
    - 成功率分析
    - 今日待执行任务
    - 异常预警
    """
    import asyncio
    return asyncio.run(_generate_daily_report_async())


async def _generate_daily_report_async() -> Dict:
    """异步生成每日报告"""
    async with AsyncSessionLocal() as db:
        try:
            now = datetime.now(timezone.utc)
            yesterday_start = (now - timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            yesterday_end = yesterday_start + timedelta(days=1)
            today_end = now + timedelta(days=1)

            # 统计昨日数据
            yesterday_published = await db.execute(
                select(func.count(ContentSchedule.id)).where(
                    and_(
                        ContentSchedule.status == ScheduleStatus.PUBLISHED,
                        ContentSchedule.actual_publish_time >= yesterday_start,
                        ContentSchedule.actual_publish_time < yesterday_end,
                    )
                )
            )
            published_count = yesterday_published.scalar() or 0

            yesterday_failed = await db.execute(
                select(func.count(ContentSchedule.id)).where(
                    and_(
                        ContentSchedule.status == ScheduleStatus.FAILED,
                        ContentSchedule.updated_at >= yesterday_start,
                        ContentSchedule.updated_at < yesterday_end,
                    )
                )
            )
            failed_count = yesterday_failed.scalar() or 0

            # 计算成功率
            total_executed = published_count + failed_count
            success_rate = (
                (published_count / total_executed * 100) if total_executed > 0 else 0
            )

            # 今日待执行任务
            today_pending = await db.execute(
                select(func.count(ContentSchedule.id)).where(
                    and_(
                        ContentSchedule.status == ScheduleStatus.PENDING,
                        ContentSchedule.scheduled_time >= now,
                        ContentSchedule.scheduled_time < today_end,
                    )
                )
            )
            pending_today = today_pending.scalar() or 0

            # 过期未执行任务
            overdue = await db.execute(
                select(func.count(ContentSchedule.id)).where(
                    and_(
                        ContentSchedule.status == ScheduleStatus.PENDING,
                        ContentSchedule.scheduled_time < now,
                    )
                )
            )
            overdue_count = overdue.scalar() or 0

            report = {
                "date": now.date().isoformat(),
                "yesterday": {
                    "published": published_count,
                    "failed": failed_count,
                    "total": total_executed,
                    "success_rate": round(success_rate, 2),
                },
                "today": {
                    "pending": pending_today,
                    "overdue": overdue_count,
                },
            }

            # 发送报告通知
            await _send_daily_report(db, report)

            logger.info(f"📊 Daily report generated: {report}")

            return report

        except Exception as e:
            logger.exception(f"Error generating daily report: {e}")
            return {"error": str(e)}


async def _send_daily_report(db, report: Dict):
    """发送每日报告给管理员"""
    try:
        yesterday_data = report["yesterday"]
        today_data = report["today"]

        message = f"""
📊 调度系统每日报告 ({report['date']})

📈 昨日执行情况:
  ✅ 成功: {yesterday_data['published']}
  ❌ 失败: {yesterday_data['failed']}
  📊 成功率: {yesterday_data['success_rate']}%

⏰ 今日计划:
  📅 待执行: {today_data['pending']}
  ⚠️ 过期未执行: {today_data['overdue']}
""".strip()

        await AdminNotificationService.notify_system_alert(
            db=db,
            alert_type="daily_schedule_report",
            severity="info",
            message="调度系统每日报告",
            details=report,
        )

        logger.info("Daily report sent to admins")

    except Exception as e:
        logger.exception(f"Failed to send daily report: {e}")


# ========== 健康检查 ==========


@celery_app.task(name="scheduler.health_check")
def health_check():
    """
    调度系统健康检查
    - 检查是否有长时间卡住的任务
    - 检查是否有异常状态
    - 检查数据库连接
    """
    import asyncio
    return asyncio.run(_health_check_async())


async def _health_check_async() -> Dict:
    """异步健康检查"""
    async with AsyncSessionLocal() as db:
        try:
            issues = []

            # 检查1: 是否有长时间处于pending但已过期的任务
            now = datetime.now(timezone.utc)
            one_hour_ago = now - timedelta(hours=1)

            stuck_schedules = await db.execute(
                select(func.count(ContentSchedule.id)).where(
                    and_(
                        ContentSchedule.status == ScheduleStatus.PENDING,
                        ContentSchedule.scheduled_time < one_hour_ago,
                    )
                )
            )
            stuck_count = stuck_schedules.scalar() or 0

            if stuck_count > 0:
                issues.append({
                    "type": "stuck_schedules",
                    "count": stuck_count,
                    "message": f"{stuck_count} schedules stuck for over 1 hour",
                })

            # 检查2: 失败率是否异常高
            recent_failures = await db.execute(
                select(func.count(ContentSchedule.id)).where(
                    and_(
                        ContentSchedule.status == ScheduleStatus.FAILED,
                        ContentSchedule.updated_at >= one_hour_ago,
                    )
                )
            )
            recent_failed = recent_failures.scalar() or 0

            if recent_failed > 10:
                issues.append({
                    "type": "high_failure_rate",
                    "count": recent_failed,
                    "message": f"{recent_failed} failures in the last hour",
                })

            health_status = "healthy" if not issues else "unhealthy"

            result = {
                "status": health_status,
                "timestamp": now.isoformat(),
                "issues": issues,
            }

            # 如果有问题，发送告警
            if issues:
                await _notify_health_issues(db, issues)
                logger.warning(f"⚠️ Health check found issues: {issues}")
            else:
                logger.info("✅ Health check passed")

            return result

        except Exception as e:
            logger.exception(f"Error in health check: {e}")
            return {"status": "error", "error": str(e)}


async def _notify_health_issues(db, issues: List[Dict]):
    """通知管理员健康检查发现的问题"""
    try:
        message = f"调度系统健康检查发现 {len(issues)} 个问题"

        await AdminNotificationService.notify_system_alert(
            db=db,
            alert_type="scheduler_health_issue",
            severity="high",
            message=message,
            details={"issues": issues},
        )

        logger.info(f"Sent health issue notification: {len(issues)} issues")

    except Exception as e:
        logger.exception(f"Failed to send health issue notification: {e}")
