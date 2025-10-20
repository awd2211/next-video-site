"""
Celery 定时任务 - 调度系统
自动执行到期的调度任务
"""

from datetime import datetime, timedelta, timezone

from celery import Task
from loguru import logger
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.scheduling import ContentSchedule, ScheduleStatus
from app.services.scheduling_service import SchedulingService

# 导入 Celery 应用
from app.celery_app import celery_app


class AsyncTask(Task):
    """异步任务基类"""

    async def run_async(self, *args, **kwargs):
        """异步执行方法（子类实现）"""
        raise NotImplementedError


@celery_app.task(name="scheduling.check_due_schedules", bind=True)
def check_due_schedules(self):
    """
    检查并执行到期的调度任务
    每分钟执行一次
    """
    import asyncio

    return asyncio.run(_check_due_schedules_async())


async def _check_due_schedules_async():
    """异步执行到期任务检查"""
    async with AsyncSessionLocal() as db:
        try:
            service = SchedulingService(db)

            # 获取所有到期任务
            due_schedules = await service.get_due_schedules()

            if not due_schedules:
                logger.debug("No due schedules found")
                return {"executed": 0, "failed": 0}

            logger.info(f"Found {len(due_schedules)} due schedules to execute")

            executed_count = 0
            failed_count = 0

            # 执行每个到期任务
            for schedule in due_schedules:
                try:
                    success, message = await service.execute_schedule(
                        schedule.id, executed_by=None  # None 表示自动执行
                    )

                    if success:
                        executed_count += 1
                        logger.info(
                            f"Schedule {schedule.id} executed successfully: {message}"
                        )
                    else:
                        failed_count += 1
                        logger.warning(
                            f"Schedule {schedule.id} execution failed: {message}"
                        )
                        # ✅ 发送失败通知
                        try:
                            from app.utils.admin_notification_service import AdminNotificationService
                            await AdminNotificationService.notify_system_alert(
                                db=db,
                                alert_type="schedule_execution_failed",
                                severity="high",
                                message=f"调度任务执行失败：{schedule.content_type.value} #{schedule.content_id}",
                                details={
                                    "schedule_id": schedule.id,
                                    "content_type": schedule.content_type.value,
                                    "content_id": schedule.content_id,
                                    "error_message": message,
                                    "scheduled_time": schedule.scheduled_time.isoformat(),
                                },
                            )
                        except Exception as notify_error:
                            logger.error(f"Failed to send failure notification: {notify_error}")

                except Exception as e:
                    failed_count += 1
                    logger.exception(
                        f"Error executing schedule {schedule.id}: {e}"
                    )
                    # ✅ 发送异常通知
                    try:
                        from app.utils.admin_notification_service import AdminNotificationService
                        await AdminNotificationService.notify_system_alert(
                            db=db,
                            alert_type="schedule_execution_error",
                            severity="high",
                            message=f"调度任务执行异常：{schedule.content_type.value} #{schedule.content_id}",
                            details={
                                "schedule_id": schedule.id,
                                "content_type": schedule.content_type.value if hasattr(schedule, 'content_type') else None,
                                "content_id": schedule.content_id if hasattr(schedule, 'content_id') else None,
                                "error": str(e),
                            },
                        )
                    except Exception as notify_error:
                        logger.error(f"Failed to send error notification: {notify_error}")

            logger.info(
                f"Scheduled publishing completed: "
                f"executed={executed_count}, failed={failed_count}"
            )

            return {"executed": executed_count, "failed": failed_count}

        except Exception as e:
            logger.exception(f"Error in check_due_schedules: {e}")
            return {"error": str(e)}


@celery_app.task(name="scheduling.check_expired_schedules", bind=True)
def check_expired_schedules(self):
    """
    检查并处理过期的调度（到达end_time的内容）
    每小时执行一次
    """
    import asyncio

    return asyncio.run(_check_expired_schedules_async())


async def _check_expired_schedules_async():
    """异步执行过期任务检查"""
    async with AsyncSessionLocal() as db:
        try:
            service = SchedulingService(db)

            # 获取所有需要过期的调度
            expired_schedules = await service.get_expired_schedules()

            if not expired_schedules:
                logger.debug("No expired schedules found")
                return {"expired": 0, "failed": 0}

            logger.info(f"Found {len(expired_schedules)} schedules to expire")

            expired_count = 0
            failed_count = 0

            # 处理每个过期任务
            for schedule in expired_schedules:
                try:
                    success = await service.expire_schedule(schedule.id)

                    if success:
                        expired_count += 1
                        logger.info(f"Schedule {schedule.id} expired successfully")
                    else:
                        failed_count += 1
                        logger.warning(f"Schedule {schedule.id} expiration failed")

                except Exception as e:
                    failed_count += 1
                    logger.exception(f"Error expiring schedule {schedule.id}: {e}")

            logger.info(
                f"Schedule expiration completed: "
                f"expired={expired_count}, failed={failed_count}"
            )

            return {"expired": expired_count, "failed": failed_count}

        except Exception as e:
            logger.exception(f"Error in check_expired_schedules: {e}")
            return {"error": str(e)}


@celery_app.task(name="scheduling.send_schedule_reminders", bind=True)
def send_schedule_reminders(self):
    """
    发送调度提醒通知
    每5分钟执行一次
    检查需要提前通知的调度任务
    """
    import asyncio

    return asyncio.run(_send_schedule_reminders_async())


async def _send_schedule_reminders_async():
    """异步执行提醒通知"""
    async with AsyncSessionLocal() as db:
        try:
            now = datetime.now(timezone.utc)
            # 查找未来30分钟内需要通知的任务
            future_time = now + timedelta(minutes=30)

            result = await db.execute(
                select(ContentSchedule).where(
                    ContentSchedule.status == ScheduleStatus.PENDING,
                    ContentSchedule.notify_before_minutes > 0,
                    ContentSchedule.notification_sent == False,
                    ContentSchedule.scheduled_time.between(now, future_time),
                )
            )

            schedules = list(result.scalars().all())

            if not schedules:
                logger.debug("No schedules need reminders")
                return {"reminders_sent": 0}

            sent_count = 0

            for schedule in schedules:
                # 检查是否到了提醒时间
                reminder_time = schedule.scheduled_time - timedelta(
                    minutes=schedule.notify_before_minutes
                )

                if now >= reminder_time and not schedule.notification_sent:
                    try:
                        # ✅ 发送通知到管理员
                        from app.utils.admin_notification_service import AdminNotificationService

                        await AdminNotificationService.notify_system_alert(
                            db=db,
                            alert_type="schedule_reminder",
                            severity="info",
                            message=f"调度任务即将执行：{schedule.content_type.value} #{schedule.content_id}",
                            details={
                                "schedule_id": schedule.id,
                                "content_type": schedule.content_type.value,
                                "content_id": schedule.content_id,
                                "scheduled_time": schedule.scheduled_time.isoformat(),
                                "notify_before_minutes": schedule.notify_before_minutes,
                            },
                        )

                        schedule.notification_sent = True
                        sent_count += 1

                        logger.info(
                            f"Reminder sent for schedule {schedule.id}, "
                            f"scheduled at {schedule.scheduled_time}"
                        )

                    except Exception as e:
                        logger.exception(
                            f"Error sending reminder for schedule {schedule.id}: {e}"
                        )

            if sent_count > 0:
                await db.commit()

            logger.info(f"Schedule reminders sent: count={sent_count}")

            return {"reminders_sent": sent_count}

        except Exception as e:
            logger.exception(f"Error in send_schedule_reminders: {e}")
            return {"error": str(e)}


@celery_app.task(name="scheduling.cleanup_old_histories", bind=True)
def cleanup_old_histories(self):
    """
    清理旧的历史记录
    每天执行一次
    保留最近90天的记录
    """
    import asyncio

    return asyncio.run(_cleanup_old_histories_async())


async def _cleanup_old_histories_async():
    """异步清理旧历史记录"""
    from app.models.scheduling import ScheduleHistory

    async with AsyncSessionLocal() as db:
        try:
            # 删除90天前的历史记录
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)

            result = await db.execute(
                select(ScheduleHistory).where(
                    ScheduleHistory.executed_at < cutoff_date
                )
            )

            old_histories = list(result.scalars().all())

            if not old_histories:
                logger.info("No old histories to clean up")
                return {"deleted": 0}

            for history in old_histories:
                await db.delete(history)

            await db.commit()

            logger.info(f"Cleaned up {len(old_histories)} old history records")

            return {"deleted": len(old_histories)}

        except Exception as e:
            logger.exception(f"Error in cleanup_old_histories: {e}")
            return {"error": str(e)}


# Celery Beat 调度配置
# 需要在 celeryconfig.py 或 main celery app 配置中添加：
"""
beat_schedule = {
    'check-due-schedules': {
        'task': 'scheduling.check_due_schedules',
        'schedule': 60.0,  # 每分钟
    },
    'check-expired-schedules': {
        'task': 'scheduling.check_expired_schedules',
        'schedule': 3600.0,  # 每小时
    },
    'send-schedule-reminders': {
        'task': 'scheduling.send_schedule_reminders',
        'schedule': 300.0,  # 每5分钟
    },
    'cleanup-old-histories': {
        'task': 'scheduling.cleanup_old_histories',
        'schedule': crontab(hour=3, minute=0),  # 每天凌晨3点
    },
}
"""


# ==================== Video & Series Scheduled Publishing ====================
# 🆕 新增：基于模型字段的定时发布（不依赖ContentSchedule表）

@celery_app.task(name="publish_scheduled_videos_and_series")
def publish_scheduled_videos_and_series():
    """
    检查并发布Video和Series的scheduled_publish_at到期内容
    每分钟执行一次
    """
    import asyncio
    return asyncio.run(_publish_scheduled_content_async())


async def _publish_scheduled_content_async():
    """异步发布定时内容（Video + Series）"""
    from app.models.video import Video, VideoStatus
    from app.models.series import Series, SeriesStatus
    from sqlalchemy import and_

    async with AsyncSessionLocal() as db:
        try:
            now = datetime.now(timezone.utc)
            videos_published = 0
            series_published = 0

            # 🎬 处理Video
            video_result = await db.execute(
                select(Video).where(
                    and_(
                        Video.scheduled_publish_at.isnot(None),
                        Video.scheduled_publish_at <= now,
                        Video.status == VideoStatus.DRAFT
                    )
                )
            )
            videos = list(video_result.scalars().all())

            for video in videos:
                video.status = VideoStatus.PUBLISHED
                video.published_at = now
                videos_published += 1
                logger.info(f"✅ Auto-published video #{video.id}: {video.title}")

            # 📺 处理Series
            series_result = await db.execute(
                select(Series).where(
                    and_(
                        Series.scheduled_publish_at.isnot(None),
                        Series.scheduled_publish_at <= now,
                        Series.status == SeriesStatus.DRAFT
                    )
                )
            )
            series_list = list(series_result.scalars().all())

            for series in series_list:
                series.status = SeriesStatus.PUBLISHED
                series.published_at = now
                series_published += 1
                logger.info(f"✅ Auto-published series #{series.id}: {series.title}")

            await db.commit()

            total = videos_published + series_published
            if total > 0:
                logger.success(
                    f"🎉 Published {videos_published} videos and {series_published} series"
                )

            return {
                "success": True,
                "videos_published": videos_published,
                "series_published": series_published,
                "total_published": total,
                "timestamp": now.isoformat()
            }

        except Exception as e:
            await db.rollback()
            logger.exception(f"❌ Failed to publish scheduled content: {e}")
            return {
                "success": False,
                "error": str(e)
            }

