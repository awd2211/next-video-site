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
        query = (
            select(ContentSchedule)
            .where(and_(*conditions) if conditions else True)
            .order_by(ContentSchedule.scheduled_time.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        schedules = list(result.scalars().all())

        # 计算总数
        count_query = select(func.count(ContentSchedule.id)).where(
            and_(*conditions) if conditions else True
        )
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
            .order_by(
                ContentSchedule.priority.desc(), ContentSchedule.scheduled_time
            )
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

        query = select(ScheduleTemplate).where(
            and_(*conditions) if conditions else True
        )

        result = await self.db.execute(query)
        templates = list(result.scalars().all())

        # 如果指定了内容类型，过滤模板
        if content_type:
            templates = [
                t for t in templates if not t.content_types or content_type in t.content_types
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

        return {
            "pending_count": pending_count,
            "published_today": published_today,
            "published_this_week": published_this_week,
            "failed_count": failed_count,
            "overdue_count": overdue_count,
            "upcoming_24h": upcoming_24h,
        }

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
        # TODO: 集成通知系统
        logger.info(
            f"Sending notifications for schedule {schedule.id} to subscribers"
        )

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
