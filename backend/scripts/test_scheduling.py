"""
测试调度系统功能
快速验证调度系统是否正常工作
"""

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.scheduling import (
    ContentSchedule,
    PublishStrategy,
    ScheduleContentType,
    ScheduleRecurrence,
    ScheduleStatus,
)
from app.models.video import Video, VideoStatus
from app.schemas.scheduling import ScheduleCreate
from app.services.scheduling_service import SchedulingService


async def create_test_video(db):
    """创建测试视频"""
    video = Video(
        title="测试视频 - 定时发布",
        slug=f"test-scheduled-video-{datetime.now().timestamp()}",
        status=VideoStatus.DRAFT,
        video_type="movie",
    )
    db.add(video)
    await db.flush()
    await db.refresh(video)
    return video


async def test_create_schedule():
    """测试创建调度"""
    print("\n1. 测试创建调度...")

    async with AsyncSessionLocal() as db:
        service = SchedulingService(db)

        # 创建测试视频
        video = await create_test_video(db)
        await db.commit()
        print(f"   创建测试视频: ID={video.id}, 标题={video.title}")

        # 创建调度（5分钟后发布）
        scheduled_time = datetime.now(timezone.utc) + timedelta(minutes=5)
        schedule_data = ScheduleCreate(
            content_type=ScheduleContentType.VIDEO,
            content_id=video.id,
            scheduled_time=scheduled_time,
            auto_publish=True,
            publish_strategy=PublishStrategy.IMMEDIATE,
            recurrence=ScheduleRecurrence.ONCE,
            title="测试调度任务",
            priority=90,
            notify_subscribers=False,
        )

        schedule = await service.create_schedule(schedule_data, created_by=5)
        print(f"   ✓ 创建调度成功: ID={schedule.id}")
        print(f"   计划时间: {schedule.scheduled_time}")
        print(f"   状态: {schedule.status.value}")

        return schedule.id, video.id


async def test_list_schedules():
    """测试获取调度列表"""
    print("\n2. 测试获取调度列表...")

    async with AsyncSessionLocal() as db:
        service = SchedulingService(db)

        schedules, total = await service.list_schedules(
            skip=0, limit=10, status=ScheduleStatus.PENDING
        )

        print(f"   找到 {total} 个待发布调度")
        for schedule in schedules[:5]:
            print(
                f"   - ID={schedule.id}, 类型={schedule.content_type.value}, "
                f"内容ID={schedule.content_id}, 时间={schedule.scheduled_time}"
            )


async def test_execute_schedule(schedule_id: int):
    """测试执行调度"""
    print(f"\n3. 测试执行调度 (ID={schedule_id})...")

    async with AsyncSessionLocal() as db:
        service = SchedulingService(db)

        # 强制执行（忽略时间限制）
        success, message = await service.execute_schedule(
            schedule_id, executed_by=5, force=True
        )

        if success:
            print(f"   ✓ 执行成功: {message}")

            # 验证视频状态
            schedule = await service.get_schedule(schedule_id)
            result = await db.execute(
                select(Video).where(Video.id == schedule.content_id)
            )
            video = result.scalar_one_or_none()

            if video:
                print(f"   视频状态已更新: {video.status.value}")
                print(f"   发布时间: {video.published_at}")
        else:
            print(f"   ✗ 执行失败: {message}")


async def test_get_statistics():
    """测试获取统计信息"""
    print("\n4. 测试获取统计信息...")

    async with AsyncSessionLocal() as db:
        service = SchedulingService(db)

        stats = await service.get_statistics()

        print(f"   待发布: {stats['pending_count']}")
        print(f"   今日已发布: {stats['published_today']}")
        print(f"   本周已发布: {stats['published_this_week']}")
        print(f"   失败: {stats['failed_count']}")
        print(f"   过期: {stats['overdue_count']}")
        print(f"   未来24小时: {stats['upcoming_24h']}")


async def test_create_template():
    """测试创建模板"""
    print("\n5. 测试创建模板...")

    from app.schemas.scheduling import TemplateCreate

    async with AsyncSessionLocal() as db:
        service = SchedulingService(db)

        template_data = TemplateCreate(
            name="每日晚8点发布",
            description="每天晚上8点自动发布视频",
            content_types=["VIDEO"],
            publish_strategy=PublishStrategy.IMMEDIATE,
            strategy_config={},
            recurrence=ScheduleRecurrence.DAILY,
            recurrence_config={"hour": 20, "minute": 0},
            notify_subscribers=True,
            notify_before_minutes=15,
        )

        template = await service.create_template(template_data, created_by=5)
        print(f"   ✓ 创建模板成功: ID={template.id}, 名称={template.name}")

        return template.id


async def test_cleanup(schedule_id: int, video_id: int):
    """清理测试数据"""
    print(f"\n6. 清理测试数据...")

    async with AsyncSessionLocal() as db:
        # 删除调度
        result = await db.execute(
            select(ContentSchedule).where(ContentSchedule.id == schedule_id)
        )
        schedule = result.scalar_one_or_none()
        if schedule:
            await db.delete(schedule)

        # 删除视频
        result = await db.execute(select(Video).where(Video.id == video_id))
        video = result.scalar_one_or_none()
        if video:
            await db.delete(video)

        await db.commit()
        print(f"   ✓ 清理完成")


async def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("调度系统功能测试")
    print("=" * 60)

    try:
        # 1. 创建调度
        schedule_id, video_id = await test_create_schedule()

        # 2. 列表查询
        await test_list_schedules()

        # 3. 执行调度
        await test_execute_schedule(schedule_id)

        # 4. 统计信息
        await test_get_statistics()

        # 5. 创建模板
        # template_id = await test_create_template()

        # 6. 清理
        await test_cleanup(schedule_id, video_id)

        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
