"""
内容调度服务层
核心业务逻辑实现
"""

import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from loguru import logger
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Announcement, Banner, Recommendation
from app.models.scheduling import (
    ContentSchedule,
    PublishStrategy,
    ScheduleContentType,
    ScheduleHistory,
    ScheduleRecurrence,
    ScheduleStatus,
    ScheduleTemplate,
)
from app.models.video import Video, VideoStatus
from app.schemas.scheduling import (
    ScheduleCreate,
    ScheduleUpdate,
    TemplateCreate,
    TemplateUpdate,
)


class SchedulingService:
    """调度服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========== 调度 CRUD ==========

    async def create_schedule(
        self, data: ScheduleCreate, created_by: int
    ) -> ContentSchedule:
        """创建调度任务"""
        # 验证内容是否存在
        await self._validate_content_exists(data.content_type, data.content_id)

        # 检查是否已存在相同的待发布调度
        existing = await self._check_duplicate_schedule(
            data.content_type, data.content_id
        )
        if existing:
            raise ValueError(
                f"Content {data.content_type}:{data.content_id} already has a pending schedule"
            )

        # 创建调度
        schedule = ContentSchedule(
            **data.model_dump(exclude={"extra_data"}),
            extra_data=data.extra_data or {},
            created_by=created_by,
            status=ScheduleStatus.PENDING,
            condition_met=True,  # 默认条件满足，后续可以添加条件检查
        )

        self.db.add(schedule)
        await self.db.flush()

        # 记录历史
        await self._add_history(
            schedule.id,
            action="created",
            status_after=ScheduleStatus.PENDING.value,
            executed_by=created_by,
            is_automatic=False,
            message=f"Schedule created for {data.content_type}:{data.content_id}",
        )

        await self.db.commit()
        await self.db.refresh(schedule)

        logger.info(
            f"Schedule created: id={schedule.id}, type={data.content_type}, "
            f"content_id={data.content_id}, time={data.scheduled_time}"
        )

        return schedule

    async def get_schedule(self, schedule_id: int) -> Optional[ContentSchedule]:
        """获取调度详情"""
        result = await self.db.execute(
            select(ContentSchedule).where(ContentSchedule.id == schedule_id)
        )
        return result.scalar_one_or_none()

    async def list_schedules(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[ScheduleStatus] = None,
        content_type: Optional[ScheduleContentType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> tuple[list[ContentSchedule], int]:
        """获取调度列表"""
        conditions = []

        if status:
            conditions.append(ContentSchedule.status == status)
        if content_type:
            conditions.append(ContentSchedule.content_type == content_type)
        if start_date:
            conditions.append(ContentSchedule.scheduled_time >= start_date)
        if end_date:
            conditions.append(ContentSchedule.scheduled_time <= end_date)

        # 查询数据
        query = select(ContentSchedule)
        if conditions:
            query = query.where(and_(*conditions))
        query = query.order_by(ContentSchedule.scheduled_time.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        schedules = list(result.scalars().all())

        # 计算总数
        count_query = select(func.count(ContentSchedule.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        return schedules, total

    async def update_schedule(
        self, schedule_id: int, data: ScheduleUpdate, updated_by: int
    ) -> ContentSchedule:
        """更新调度"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            raise ValueError(f"Schedule {schedule_id} not found")

        if schedule.status != ScheduleStatus.PENDING:
            raise ValueError(
                f"Cannot update schedule with status {schedule.status.value}"
            )

        # 更新字段
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in update_data.items():
            setattr(schedule, key, value)

        schedule.updated_by = updated_by

        # 记录历史
        await self._add_history(
            schedule_id,
            action="updated",
            status_before=schedule.status.value,
            status_after=schedule.status.value,
            executed_by=updated_by,
            is_automatic=False,
            message="Schedule updated",
            details=update_data,
        )

        await self.db.commit()
        await self.db.refresh(schedule)

        logger.info(f"Schedule updated: id={schedule_id}, updates={update_data}")

        return schedule

    async def cancel_schedule(
        self, schedule_id: int, cancelled_by: int, reason: Optional[str] = None
    ) -> ContentSchedule:
        """取消调度"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            raise ValueError(f"Schedule {schedule_id} not found")

        if schedule.status not in [ScheduleStatus.PENDING, ScheduleStatus.FAILED]:
            raise ValueError(
                f"Cannot cancel schedule with status {schedule.status.value}"
            )

        old_status = schedule.status
        schedule.status = ScheduleStatus.CANCELLED
        schedule.updated_by = cancelled_by

        # 记录历史
        await self._add_history(
            schedule_id,
            action="cancelled",
            status_before=old_status.value,
            status_after=ScheduleStatus.CANCELLED.value,
            executed_by=cancelled_by,
            is_automatic=False,
            message=reason or "Schedule cancelled",
        )

        await self.db.commit()
        await self.db.refresh(schedule)

        logger.info(f"Schedule cancelled: id={schedule_id}, reason={reason}")

        return schedule

    async def delete_schedule(self, schedule_id: int) -> bool:
        """删除调度（物理删除）"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return False

        await self.db.delete(schedule)
        await self.db.commit()

        logger.info(f"Schedule deleted: id={schedule_id}")

        return True

    # ========== 执行相关 ==========

    async def execute_schedule(
        self,
        schedule_id: int,
        executed_by: Optional[int] = None,
        force: bool = False,
    ) -> tuple[bool, str]:
        """执行调度任务"""
        start_time = time.time()

        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return False, "Schedule not found"

        if schedule.status != ScheduleStatus.PENDING:
            return False, f"Schedule status is {schedule.status.value}, not PENDING"

        # 检查条件（除非强制执行）
        if not force and not schedule.condition_met:
            return False, "Schedule condition not met"

        try:
            # 根据内容类型执行相应操作
            success = await self._execute_by_content_type(schedule)

            if success:
                # 更新调度状态
                old_status = schedule.status
                schedule.status = ScheduleStatus.PUBLISHED
                schedule.actual_publish_time = datetime.now(timezone.utc)

                # 处理重复任务
                if schedule.recurrence != ScheduleRecurrence.ONCE:
                    await self._create_next_occurrence(schedule)

                # 发送通知
                if schedule.notify_subscribers:
                    await self._send_subscriber_notifications(schedule)

                # 记录历史
                execution_time = int((time.time() - start_time) * 1000)
                await self._add_history(
                    schedule_id,
                    action="published",
                    status_before=old_status.value,
                    status_after=ScheduleStatus.PUBLISHED.value,
                    executed_by=executed_by,
                    is_automatic=executed_by is None,
                    message="Schedule executed successfully",
                    execution_time_ms=execution_time,
                )

                await self.db.commit()
                await self.db.refresh(schedule)

                logger.info(
                    f"Schedule executed successfully: id={schedule_id}, "
                    f"time={execution_time}ms"
                )

                return True, "Schedule executed successfully"
            else:
                # 执行失败，增加重试次数
                schedule.retry_count += 1
                if schedule.retry_count >= schedule.max_retry:
                    schedule.status = ScheduleStatus.FAILED
                    schedule.error_message = "Max retry attempts reached"

                await self._add_history(
                    schedule_id,
                    action="failed",
                    status_before=ScheduleStatus.PENDING.value,
                    status_after=schedule.status.value,
                    executed_by=executed_by,
                    is_automatic=executed_by is None,
                    success=False,
                    message="Schedule execution failed",
                )

                await self.db.commit()

                logger.error(f"Schedule execution failed: id={schedule_id}")

                return False, "Schedule execution failed"

        except Exception as e:
            logger.exception(f"Error executing schedule {schedule_id}: {e}")

            # 记录错误
            schedule.retry_count += 1
            schedule.error_message = str(e)
            if schedule.retry_count >= schedule.max_retry:
                schedule.status = ScheduleStatus.FAILED

            await self._add_history(
                schedule_id,
                action="failed",
                status_before=ScheduleStatus.PENDING.value,
                status_after=schedule.status.value,
                executed_by=executed_by,
                is_automatic=executed_by is None,
                success=False,
                message=f"Exception: {str(e)}",
            )

            await self.db.commit()

            return False, f"Error: {str(e)}"

    async def get_due_schedules(self) -> list[ContentSchedule]:
        """获取所有到期的调度任务"""
        now = datetime.now(timezone.utc)

        result = await self.db.execute(
            select(ContentSchedule)
            .where(
                and_(
                    ContentSchedule.status == ScheduleStatus.PENDING,
                    ContentSchedule.scheduled_time <= now,
                    ContentSchedule.condition_met == True,
                    ContentSchedule.auto_publish == True,
                )
            )
            .order_by(ContentSchedule.priority.desc(), ContentSchedule.scheduled_time)
        )

        return list(result.scalars().all())

    async def get_expired_schedules(self) -> list[ContentSchedule]:
        """获取所有需要过期的调度（到达end_time）"""
        now = datetime.now(timezone.utc)

        result = await self.db.execute(
            select(ContentSchedule).where(
                and_(
                    ContentSchedule.status == ScheduleStatus.PUBLISHED,
                    ContentSchedule.end_time.isnot(None),
                    ContentSchedule.end_time <= now,
                    ContentSchedule.auto_expire == True,
                )
            )
        )

        return list(result.scalars().all())

    async def expire_schedule(self, schedule_id: int) -> bool:
        """使调度过期（下线内容）"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return False

        try:
            # 根据内容类型下线
            success = await self._expire_by_content_type(schedule)

            if success:
                old_status = schedule.status
                schedule.status = ScheduleStatus.EXPIRED

                await self._add_history(
                    schedule_id,
                    action="expired",
                    status_before=old_status.value,
                    status_after=ScheduleStatus.EXPIRED.value,
                    is_automatic=True,
                    message="Schedule expired and content unpublished",
                )

                await self.db.commit()

                logger.info(f"Schedule expired: id={schedule_id}")

                return True

        except Exception as e:
            logger.exception(f"Error expiring schedule {schedule_id}: {e}")

        return False

    # ========== 模板管理 ==========

    async def create_template(
        self, data: TemplateCreate, created_by: int
    ) -> ScheduleTemplate:
        """创建模板"""
        template = ScheduleTemplate(
            **data.model_dump(),
            created_by=created_by,
            is_active=True,
            is_system=False,
            usage_count=0,
        )

        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)

        logger.info(f"Template created: id={template.id}, name={data.name}")

        return template

    async def get_template(self, template_id: int) -> Optional[ScheduleTemplate]:
        """获取模板"""
        result = await self.db.execute(
            select(ScheduleTemplate).where(ScheduleTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    async def list_templates(
        self, is_active: Optional[bool] = None, content_type: Optional[str] = None
    ) -> list[ScheduleTemplate]:
        """获取模板列表"""
        conditions = []

        if is_active is not None:
            conditions.append(ScheduleTemplate.is_active == is_active)

        query = select(ScheduleTemplate)
        if conditions:
            query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        templates = list(result.scalars().all())

        # 如果指定了内容类型，过滤模板
        if content_type:
            templates = [
                t
                for t in templates
                if not t.content_types or content_type in t.content_types
            ]

        return templates

    async def apply_template(
        self,
        template_id: int,
        content_type: ScheduleContentType,
        content_id: int,
        scheduled_time: datetime,
        created_by: int,
        overrides: Optional[dict[str, Any]] = None,
    ) -> ContentSchedule:
        """应用模板创建调度"""
        template = await self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")

        if not template.is_active:
            raise ValueError("Template is not active")

        # 使用模板数据创建调度
        schedule_data = ScheduleCreate(
            content_type=content_type,
            content_id=content_id,
            scheduled_time=scheduled_time,
            publish_strategy=template.publish_strategy,
            strategy_config=template.strategy_config,
            recurrence=template.recurrence,
            recurrence_config=template.recurrence_config,
            notify_subscribers=template.notify_subscribers,
            notify_before_minutes=template.notify_before_minutes,
            **(overrides or {}),
        )

        schedule = await self.create_schedule(schedule_data, created_by)

        # 增加模板使用次数
        template.usage_count += 1
        await self.db.commit()

        logger.info(
            f"Template applied: template_id={template_id}, schedule_id={schedule.id}"
        )

        return schedule

    # ========== 统计分析 ==========

    async def get_statistics(self) -> dict[str, Any]:
        """获取统计信息"""
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())

        # 待发布数量
        pending_result = await self.db.execute(
            select(func.count(ContentSchedule.id)).where(
                ContentSchedule.status == ScheduleStatus.PENDING
            )
        )
        pending_count = pending_result.scalar() or 0

        # 今日已发布
        published_today_result = await self.db.execute(
            select(func.count(ContentSchedule.id)).where(
                and_(
                    ContentSchedule.status == ScheduleStatus.PUBLISHED,
                    ContentSchedule.actual_publish_time >= today_start,
                )
            )
        )
        published_today = published_today_result.scalar() or 0

        # 本周已发布
        published_week_result = await self.db.execute(
            select(func.count(ContentSchedule.id)).where(
                and_(
                    ContentSchedule.status == ScheduleStatus.PUBLISHED,
                    ContentSchedule.actual_publish_time >= week_start,
                )
            )
        )
        published_this_week = published_week_result.scalar() or 0

        # 失败数量
        failed_result = await self.db.execute(
            select(func.count(ContentSchedule.id)).where(
                ContentSchedule.status == ScheduleStatus.FAILED
            )
        )
        failed_count = failed_result.scalar() or 0

        # 过期数量
        overdue_result = await self.db.execute(
            select(func.count(ContentSchedule.id)).where(
                and_(
                    ContentSchedule.status == ScheduleStatus.PENDING,
                    ContentSchedule.scheduled_time < now,
                )
            )
        )
        overdue_count = overdue_result.scalar() or 0

        # 未来24小时
        upcoming_24h_result = await self.db.execute(
            select(func.count(ContentSchedule.id)).where(
                and_(
                    ContentSchedule.status == ScheduleStatus.PENDING,
                    ContentSchedule.scheduled_time.between(
                        now, now + timedelta(hours=24)
                    ),
                )
            )
        )
        upcoming_24h = upcoming_24h_result.scalar() or 0

        # 按内容类型统计
        by_content_type_result = await self.db.execute(
            select(
                ContentSchedule.content_type,
                func.count(ContentSchedule.id).label("count"),
            ).group_by(ContentSchedule.content_type)
        )
        by_content_type = {
            row.content_type.value: row.count for row in by_content_type_result
        }

        # 按状态统计
        by_status_result = await self.db.execute(
            select(
                ContentSchedule.status, func.count(ContentSchedule.id).label("count")
            ).group_by(ContentSchedule.status)
        )
        by_status = {row.status.value: row.count for row in by_status_result}

        # 按发布策略统计
        by_strategy_result = await self.db.execute(
            select(
                ContentSchedule.publish_strategy,
                func.count(ContentSchedule.id).label("count"),
            ).group_by(ContentSchedule.publish_strategy)
        )
        by_strategy = {
            row.publish_strategy.value: row.count for row in by_strategy_result
        }

        # 计算总数
        total_result = await self.db.execute(
            select(func.count(ContentSchedule.id))
        )
        total = total_result.scalar() or 0

        return {
            "total": total,
            "pending_count": pending_count,
            "published_today": published_today,
            "published_this_week": published_this_week,
            "failed_count": failed_count,
            "overdue_count": overdue_count,
            "upcoming_24h": upcoming_24h,
            "by_content_type": by_content_type,
            "by_status": by_status,
            "by_strategy": by_strategy,
        }

    async def get_calendar_data(self, year: int, month: int) -> list[dict[str, Any]]:
        """获取日历数据"""
        from calendar import monthrange

        # 计算月份的开始和结束日期
        month_start = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
        _, last_day = monthrange(year, month)
        month_end = datetime(
            year, month, last_day, 23, 59, 59, 999999, tzinfo=timezone.utc
        )

        # 查询这个月的所有调度
        result = await self.db.execute(
            select(ContentSchedule)
            .where(
                and_(
                    ContentSchedule.scheduled_time >= month_start,
                    ContentSchedule.scheduled_time <= month_end,
                )
            )
            .order_by(ContentSchedule.scheduled_time)
        )
        schedules = result.scalars().all()

        # 转换为日历事件格式
        events = []
        for schedule in schedules:
            # 根据状态选择颜色
            color_map = {
                ScheduleStatus.PENDING: "#faad14",  # 橙色
                ScheduleStatus.PUBLISHED: "#52c41a",  # 绿色
                ScheduleStatus.FAILED: "#ff4d4f",  # 红色
                ScheduleStatus.CANCELLED: "#d9d9d9",  # 灰色
                ScheduleStatus.EXPIRED: "#8c8c8c",  # 深灰色
            }

            events.append(
                {
                    "id": schedule.id,
                    "title": schedule.title
                    or f"{schedule.content_type.value} #{schedule.content_id}",
                    "content_type": schedule.content_type.value,
                    "scheduled_time": schedule.scheduled_time.isoformat(),
                    "end_time": (
                        schedule.end_time.isoformat() if schedule.end_time else None
                    ),
                    "status": schedule.status.value,
                    "priority": schedule.priority,
                    "color": color_map.get(schedule.status, "#1890ff"),
                }
            )

        return events

    async def get_suggested_times(
        self, content_type: ScheduleContentType
    ) -> list[dict[str, Any]]:
        """智能推荐最佳发布时间"""
        # 查询过去30天的发布数据
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

        # 按小时统计发布成功率
        result = await self.db.execute(
            select(
                func.extract("hour", ContentSchedule.actual_publish_time).label("hour"),
                func.count(ContentSchedule.id).label("count"),
            )
            .where(
                and_(
                    ContentSchedule.content_type == content_type,
                    ContentSchedule.status == ScheduleStatus.PUBLISHED,
                    ContentSchedule.actual_publish_time >= thirty_days_ago,
                )
            )
            .group_by("hour")
            .order_by(func.count(ContentSchedule.id).desc())
        )

        hourly_data = result.all()

        if not hourly_data:
            # 如果没有历史数据，返回默认推荐时间
            return [
                {"hour": 20, "score": 95.0, "reason": "用户活跃高峰期（默认推荐）"},
                {"hour": 12, "score": 90.0, "reason": "午间流量高峰（默认推荐）"},
                {"hour": 21, "score": 85.0, "reason": "晚间黄金时段（默认推荐）"},
            ]

        # 计算评分（基于发布次数的百分比）
        max_count = max(row.count for row in hourly_data) if hourly_data else 1
        suggestions = []

        for row in hourly_data[:3]:  # 取前3个最佳时段
            hour = int(row.hour)
            count = row.count
            score = (count / max_count) * 100

            # 根据时段生成理由
            reason = ""
            if 19 <= hour <= 23:
                reason = "晚间黄金时段，用户活跃度最高"
            elif 12 <= hour <= 14:
                reason = "午间休息时段，流量增长明显"
            elif 8 <= hour <= 10:
                reason = "早高峰时段，上班途中观看"
            elif 18 <= hour <= 19:
                reason = "下班时段，流量开始上升"
            else:
                reason = f"历史数据显示 {hour}:00 发布效果较好"

            suggestions.append(
                {"hour": hour, "score": round(score, 1), "reason": reason}
            )

        return suggestions

    async def get_analytics(self) -> dict[str, Any]:
        """获取调度分析数据"""
        from datetime import timedelta

        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)

        # 1. 计算成功率（过去30天）
        published_result = await self.db.execute(
            select(func.count(ContentSchedule.id)).where(
                and_(
                    ContentSchedule.status == ScheduleStatus.PUBLISHED,
                    ContentSchedule.actual_publish_time >= thirty_days_ago,
                )
            )
        )
        published_count = published_result.scalar() or 0

        failed_result = await self.db.execute(
            select(func.count(ContentSchedule.id)).where(
                and_(
                    ContentSchedule.status == ScheduleStatus.FAILED,
                    ContentSchedule.updated_at >= thirty_days_ago,
                )
            )
        )
        failed_count = failed_result.scalar() or 0

        total_executed = published_count + failed_count
        success_rate = (
            (published_count / total_executed * 100) if total_executed > 0 else 0.0
        )

        # 2. 平均执行时间（从历史记录中获取）
        avg_time_result = await self.db.execute(
            select(func.avg(ScheduleHistory.execution_time_ms)).where(
                and_(
                    ScheduleHistory.success == True,
                    ScheduleHistory.execution_time_ms.isnot(None),
                    ScheduleHistory.executed_at >= thirty_days_ago,
                )
            )
        )
        avg_execution_time = avg_time_result.scalar() or 0.0

        # 3. 发布高峰时段（统计发布最多的3个小时）
        peak_hours_result = await self.db.execute(
            select(
                func.extract("hour", ContentSchedule.actual_publish_time).label("hour"),
                func.count(ContentSchedule.id).label("count"),
            )
            .where(
                and_(
                    ContentSchedule.status == ScheduleStatus.PUBLISHED,
                    ContentSchedule.actual_publish_time >= thirty_days_ago,
                )
            )
            .group_by("hour")
            .order_by(func.count(ContentSchedule.id).desc())
            .limit(3)
        )
        peak_hours = [int(row.hour) for row in peak_hours_result]

        # 4. 最佳发布策略（成功率最高的策略）
        strategy_stats_result = await self.db.execute(
            select(
                ContentSchedule.publish_strategy,
                func.count(ContentSchedule.id).label("total"),
                func.sum(
                    func.case(
                        (ContentSchedule.status == ScheduleStatus.PUBLISHED, 1), else_=0
                    )
                ).label("success"),
            )
            .where(ContentSchedule.updated_at >= thirty_days_ago)
            .group_by(ContentSchedule.publish_strategy)
        )

        best_strategy = None
        best_rate = 0.0
        for row in strategy_stats_result:
            if row.total > 0:
                rate = (row.success / row.total) * 100
                if rate > best_rate:
                    best_rate = rate
                    best_strategy = row.publish_strategy.value

        # 5. 每周趋势（过去7天每天的发布数量）
        weekly_trends = {}
        for i in range(7):
            day = now - timedelta(days=i)
            day_name = day.strftime("%A").lower()  # monday, tuesday, etc.
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            # 统计每4小时的发布量
            hourly_counts = []
            for hour_offset in [0, 4, 8, 12, 16, 20]:
                period_start = day_start + timedelta(hours=hour_offset)
                period_end = period_start + timedelta(hours=4)

                count_result = await self.db.execute(
                    select(func.count(ContentSchedule.id)).where(
                        and_(
                            ContentSchedule.status == ScheduleStatus.PUBLISHED,
                            ContentSchedule.actual_publish_time >= period_start,
                            ContentSchedule.actual_publish_time < period_end,
                        )
                    )
                )
                hourly_counts.append(count_result.scalar() or 0)

            weekly_trends[day_name] = hourly_counts

        return {
            "success_rate": round(success_rate, 2),
            "avg_execution_time_ms": round(avg_execution_time, 2),
            "peak_hours": peak_hours,
            "best_performing_strategy": best_strategy or "immediate",
            "weekly_trends": weekly_trends,
        }

    async def get_schedule_history(
        self, schedule_id: int, skip: int = 0, limit: int = 50
    ) -> tuple[list[ScheduleHistory], int]:
        """获取调度历史记录"""
        # 查询历史记录
        query = (
            select(ScheduleHistory)
            .where(ScheduleHistory.schedule_id == schedule_id)
            .order_by(ScheduleHistory.executed_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        histories = list(result.scalars().all())

        # 计算总数
        count_query = select(func.count(ScheduleHistory.id)).where(
            ScheduleHistory.schedule_id == schedule_id
        )
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        return histories, total

    async def list_all_histories(
        self,
        skip: int = 0,
        limit: int = 50,
        action: Optional[str] = None,
        content_type: Optional[ScheduleContentType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> tuple[list[ScheduleHistory], int]:
        """获取所有历史记录（支持过滤）"""
        # 构建连接查询
        query = select(ScheduleHistory).join(
            ContentSchedule, ScheduleHistory.schedule_id == ContentSchedule.id
        )

        conditions = []
        if action:
            conditions.append(ScheduleHistory.action == action)
        if content_type:
            conditions.append(ContentSchedule.content_type == content_type)
        if start_date:
            conditions.append(ScheduleHistory.executed_at >= start_date)
        if end_date:
            conditions.append(ScheduleHistory.executed_at <= end_date)

        if conditions:
            query = query.where(and_(*conditions))

        query = (
            query.order_by(ScheduleHistory.executed_at.desc()).offset(skip).limit(limit)
        )

        result = await self.db.execute(query)
        histories = list(result.scalars().all())

        # 计算总数
        count_query = select(func.count(ScheduleHistory.id)).join(
            ContentSchedule, ScheduleHistory.schedule_id == ContentSchedule.id
        )
        if conditions:
            count_query = count_query.where(and_(*conditions))

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        return histories, total

    # ========== 私有辅助方法 ==========

    async def _validate_content_exists(
        self, content_type: ScheduleContentType, content_id: int
    ) -> bool:
        """验证内容是否存在"""
        model_map = {
            ScheduleContentType.VIDEO: Video,
            ScheduleContentType.BANNER: Banner,
            ScheduleContentType.ANNOUNCEMENT: Announcement,
            ScheduleContentType.RECOMMENDATION: Recommendation,
        }

        model = model_map.get(content_type)
        if not model:
            raise ValueError(f"Unsupported content type: {content_type}")

        result = await self.db.execute(select(model).where(model.id == content_id))
        content = result.scalar_one_or_none()

        if not content:
            raise ValueError(f"{content_type} with id {content_id} not found")

        return True

    async def _check_duplicate_schedule(
        self, content_type: ScheduleContentType, content_id: int
    ) -> Optional[ContentSchedule]:
        """检查是否已存在待发布的调度"""
        result = await self.db.execute(
            select(ContentSchedule).where(
                and_(
                    ContentSchedule.content_type == content_type,
                    ContentSchedule.content_id == content_id,
                    ContentSchedule.status == ScheduleStatus.PENDING,
                )
            )
        )
        return result.scalar_one_or_none()

    async def _execute_by_content_type(self, schedule: ContentSchedule) -> bool:
        """根据内容类型执行发布"""
        try:
            if schedule.content_type == ScheduleContentType.VIDEO:
                return await self._publish_video(schedule.content_id)
            elif schedule.content_type == ScheduleContentType.BANNER:
                return await self._activate_banner(schedule.content_id)
            elif schedule.content_type == ScheduleContentType.ANNOUNCEMENT:
                return await self._publish_announcement(schedule.content_id)
            elif schedule.content_type == ScheduleContentType.RECOMMENDATION:
                return await self._update_recommendation(schedule.content_id)
            else:
                logger.warning(f"Unsupported content type: {schedule.content_type}")
                return False
        except Exception as e:
            logger.exception(f"Error in _execute_by_content_type: {e}")
            return False

    async def _publish_video(self, video_id: int) -> bool:
        """发布视频"""
        result = await self.db.execute(select(Video).where(Video.id == video_id))
        video = result.scalar_one_or_none()

        if not video:
            return False

        video.status = VideoStatus.PUBLISHED
        video.published_at = datetime.now(timezone.utc)
        await self.db.flush()

        logger.info(f"Video published: id={video_id}")
        return True

    async def _activate_banner(self, banner_id: int) -> bool:
        """激活横幅"""
        result = await self.db.execute(select(Banner).where(Banner.id == banner_id))
        banner = result.scalar_one_or_none()

        if not banner:
            return False

        from app.models.content import BannerStatus

        banner.status = BannerStatus.ACTIVE
        await self.db.flush()

        logger.info(f"Banner activated: id={banner_id}")
        return True

    async def _publish_announcement(self, announcement_id: int) -> bool:
        """发布公告"""
        result = await self.db.execute(
            select(Announcement).where(Announcement.id == announcement_id)
        )
        announcement = result.scalar_one_or_none()

        if not announcement:
            return False

        announcement.is_active = True
        await self.db.flush()

        logger.info(f"Announcement published: id={announcement_id}")
        return True

    async def _update_recommendation(self, recommendation_id: int) -> bool:
        """更新推荐位"""
        result = await self.db.execute(
            select(Recommendation).where(Recommendation.id == recommendation_id)
        )
        recommendation = result.scalar_one_or_none()

        if not recommendation:
            return False

        recommendation.is_active = True
        await self.db.flush()

        logger.info(f"Recommendation updated: id={recommendation_id}")
        return True

    async def _expire_by_content_type(self, schedule: ContentSchedule) -> bool:
        """根据内容类型下线内容"""
        try:
            if schedule.content_type == ScheduleContentType.BANNER:
                return await self._deactivate_banner(schedule.content_id)
            elif schedule.content_type == ScheduleContentType.ANNOUNCEMENT:
                return await self._deactivate_announcement(schedule.content_id)
            elif schedule.content_type == ScheduleContentType.RECOMMENDATION:
                return await self._deactivate_recommendation(schedule.content_id)
            # 视频一般不自动下线
            return True
        except Exception as e:
            logger.exception(f"Error in _expire_by_content_type: {e}")
            return False

    async def _deactivate_banner(self, banner_id: int) -> bool:
        """停用横幅"""
        result = await self.db.execute(select(Banner).where(Banner.id == banner_id))
        banner = result.scalar_one_or_none()

        if banner:
            from app.models.content import BannerStatus

            banner.status = BannerStatus.INACTIVE
            await self.db.flush()
            logger.info(f"Banner deactivated: id={banner_id}")
            return True
        return False

    async def _deactivate_announcement(self, announcement_id: int) -> bool:
        """停用公告"""
        result = await self.db.execute(
            select(Announcement).where(Announcement.id == announcement_id)
        )
        announcement = result.scalar_one_or_none()

        if announcement:
            announcement.is_active = False
            await self.db.flush()
            logger.info(f"Announcement deactivated: id={announcement_id}")
            return True
        return False

    async def _deactivate_recommendation(self, recommendation_id: int) -> bool:
        """停用推荐位"""
        result = await self.db.execute(
            select(Recommendation).where(Recommendation.id == recommendation_id)
        )
        recommendation = result.scalar_one_or_none()

        if recommendation:
            recommendation.is_active = False
            await self.db.flush()
            logger.info(f"Recommendation deactivated: id={recommendation_id}")
            return True
        return False

    async def _create_next_occurrence(self, schedule: ContentSchedule) -> None:
        """创建下一次重复任务"""
        # 计算下次执行时间
        next_time = self._calculate_next_occurrence(
            schedule.scheduled_time, schedule.recurrence, schedule.recurrence_config
        )

        if next_time:
            # 创建新的调度
            new_schedule = ContentSchedule(
                content_type=schedule.content_type,
                content_id=schedule.content_id,
                scheduled_time=next_time,
                status=ScheduleStatus.PENDING,
                auto_publish=schedule.auto_publish,
                auto_expire=schedule.auto_expire,
                publish_strategy=schedule.publish_strategy,
                strategy_config=schedule.strategy_config,
                recurrence=schedule.recurrence,
                recurrence_config=schedule.recurrence_config,
                notify_subscribers=schedule.notify_subscribers,
                notify_before_minutes=schedule.notify_before_minutes,
                priority=schedule.priority,
                title=schedule.title,
                description=schedule.description,
                created_by=schedule.created_by,
                condition_met=True,
            )

            self.db.add(new_schedule)
            await self.db.flush()

            logger.info(
                f"Next occurrence created: id={new_schedule.id}, time={next_time}"
            )

    def _calculate_next_occurrence(
        self,
        current_time: datetime,
        recurrence: ScheduleRecurrence,
        config: dict[str, Any],
    ) -> Optional[datetime]:
        """计算下次执行时间"""
        if recurrence == ScheduleRecurrence.ONCE:
            return None
        elif recurrence == ScheduleRecurrence.DAILY:
            return current_time + timedelta(days=1)
        elif recurrence == ScheduleRecurrence.WEEKLY:
            return current_time + timedelta(weeks=1)
        elif recurrence == ScheduleRecurrence.MONTHLY:
            # 简单实现：加30天（可根据配置优化）
            return current_time + timedelta(days=30)
        return None

    async def _send_subscriber_notifications(self, schedule: ContentSchedule) -> None:
        """发送订阅者通知"""
        try:
            from app.utils.admin_notification_service import AdminNotificationService

            # 映射内容类型
            content_type_map = {
                ScheduleContentType.VIDEO: "video",
                ScheduleContentType.BANNER: "banner",
                ScheduleContentType.ANNOUNCEMENT: "announcement",
                ScheduleContentType.RECOMMENDATION: "recommendation",
            }

            content_type_str = content_type_map.get(schedule.content_type, "content")
            content_title = (
                schedule.title
                or f"{schedule.content_type.value} #{schedule.content_id}"
            )

            # 发送定时内容发布通知
            await AdminNotificationService.notify_scheduled_content(
                db=self.db,
                content_id=schedule.content_id,
                content_title=content_title,
                content_type=content_type_str,
                action="published",
                scheduled_time=(
                    schedule.scheduled_time.isoformat()
                    if schedule.scheduled_time
                    else None
                ),
                admin_username=None,  # 自动发布，无管理员
            )

            logger.info(
                f"Sent admin notification for schedule {schedule.id}: "
                f"{content_type_str} #{schedule.content_id} published"
            )

        except Exception as e:
            logger.error(
                f"Failed to send subscriber notifications for schedule {schedule.id}: {e}"
            )
            # 不影响主流程，继续执行

    async def _add_history(
        self,
        schedule_id: int,
        action: str,
        status_after: str,
        status_before: Optional[str] = None,
        executed_by: Optional[int] = None,
        is_automatic: bool = True,
        success: bool = True,
        message: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        execution_time_ms: Optional[int] = None,
    ) -> None:
        """添加历史记录"""
        history = ScheduleHistory(
            schedule_id=schedule_id,
            action=action,
            status_before=status_before,
            status_after=status_after,
            success=success,
            message=message,
            details=details or {},
            executed_by=executed_by,
            is_automatic=is_automatic,
            execution_time_ms=execution_time_ms,
        )

        self.db.add(history)
        await self.db.flush()
