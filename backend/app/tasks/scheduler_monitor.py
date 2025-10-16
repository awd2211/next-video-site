"""
调度任务监控器
负责生成报告和健康检查
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List

from loguru import logger
from sqlalchemy import and_, func, select

from app.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models.scheduling import ContentSchedule, ScheduleStatus
from app.utils.admin_notification_service import AdminNotificationService


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
