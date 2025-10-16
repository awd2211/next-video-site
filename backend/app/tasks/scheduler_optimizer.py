"""
调度任务优化器
负责智能优化调度时间和检测冲突
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List

from loguru import logger
from sqlalchemy import and_, select

from app.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models.scheduling import ContentSchedule, ScheduleStatus
from app.utils.admin_notification_service import AdminNotificationService


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

            # 如果某个小时超过10个任务，自动分散
            optimized_count = 0
            if max_load > 10:
                logger.info(
                    f"High load detected at hour {max_load_hour}: {max_load} tasks"
                )

                # ✅ 实现任务重新分配逻辑
                # 策略：将高峰时段的后半部分任务分散到相邻小时
                peak_schedules = [s for s in schedules if s.scheduled_time.hour == max_load_hour]

                # 按时间排序，保留前10个，其余分散
                peak_schedules.sort(key=lambda x: x.scheduled_time)
                schedules_to_redistribute = peak_schedules[10:]  # 超过10个的部分

                # 查找相邻小时的负载
                prev_hour = (max_load_hour - 1) % 24
                next_hour = (max_load_hour + 1) % 24

                prev_load = hourly_counts.get(prev_hour, 0)
                next_load = hourly_counts.get(next_hour, 0)

                for i, schedule in enumerate(schedules_to_redistribute):
                    try:
                        # 交替分配到前一小时和后一小时（选择负载较轻的）
                        if prev_load < next_load or (prev_load == next_load and i % 2 == 0):
                            # 分配到前一小时
                            offset_hours = -1
                            prev_load += 1
                        else:
                            # 分配到后一小时
                            offset_hours = 1
                            next_load += 1

                        # 计算新时间（保持分钟和秒不变，只调整小时）
                        new_time = schedule.scheduled_time + timedelta(hours=offset_hours)

                        # 更新调度时间
                        schedule.scheduled_time = new_time
                        optimized_count += 1

                        logger.info(
                            f"Redistributed schedule {schedule.id} from hour {max_load_hour} "
                            f"to hour {new_time.hour}"
                        )

                    except Exception as e:
                        logger.error(f"Failed to redistribute schedule {schedule.id}: {e}")

                # 提交更改
                if optimized_count > 0:
                    await db.commit()
                    logger.info(f"Successfully redistributed {optimized_count} schedules")

                    # 发送优化通知
                    await AdminNotificationService.notify_system_alert(
                        db=db,
                        alert_type="schedule_optimization",
                        severity="info",
                        message=f"已优化调度负载：{optimized_count} 个任务从高峰时段分散",
                        details={
                            "original_peak_hour": max_load_hour,
                            "original_peak_load": max_load,
                            "redistributed_count": optimized_count,
                            "new_distribution": {
                                "prev_hour_load": prev_load,
                                "next_hour_load": next_load,
                            },
                        },
                    )

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
