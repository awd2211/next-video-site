"""
调度任务执行器
负责执行到期的调度任务
"""

from datetime import datetime, timezone
from typing import Dict, List

from loguru import logger
from sqlalchemy import and_

from app.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models.scheduling import ContentSchedule, ScheduleStatus
from app.services.scheduling_service import SchedulingService
from app.utils.admin_notification_service import AdminNotificationService


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
