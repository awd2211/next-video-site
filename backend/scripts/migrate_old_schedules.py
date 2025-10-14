"""
迁移旧的视频定时发布数据到新的调度系统
将 video.scheduled_publish_at 字段迁移到 content_schedules 表
"""

import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.scheduling import (
    PublishStrategy,
    ScheduleContentType,
    ScheduleRecurrence,
    ScheduleStatus,
)
from app.models.video import Video, VideoStatus
from app.services.scheduling_service import SchedulingService
from app.schemas.scheduling import ScheduleCreate


async def migrate_old_schedules():
    """迁移旧的视频定时发布"""
    async with AsyncSessionLocal() as db:
        service = SchedulingService(db)

        # 查找所有有 scheduled_publish_at 的视频
        result = await db.execute(
            select(Video).where(Video.scheduled_publish_at.isnot(None))
        )
        videos = list(result.scalars().all())

        if not videos:
            print("没有找到需要迁移的视频")
            return

        print(f"找到 {len(videos)} 个视频需要迁移")

        success_count = 0
        failed_count = 0

        for video in videos:
            try:
                # 检查是否已经迁移过
                existing = await db.execute(
                    select(ScheduleContentType).where(
                        ScheduleContentType.content_type == ScheduleContentType.VIDEO,
                        ScheduleContentType.content_id == video.id,
                    )
                )
                if existing.scalar_one_or_none():
                    print(f"  跳过视频 {video.id} (已存在调度记录)")
                    continue

                # 确定状态
                now = datetime.now(timezone.utc)
                if video.scheduled_publish_at > now:
                    status = ScheduleStatus.PENDING
                else:
                    # 已过期的，根据视频当前状态判断
                    status = (
                        ScheduleStatus.PUBLISHED
                        if video.status == VideoStatus.PUBLISHED
                        else ScheduleStatus.PENDING
                    )

                # 创建调度记录
                schedule_data = ScheduleCreate(
                    content_type=ScheduleContentType.VIDEO,
                    content_id=video.id,
                    scheduled_time=video.scheduled_publish_at,
                    auto_publish=True,
                    publish_strategy=PublishStrategy.IMMEDIATE,
                    recurrence=ScheduleRecurrence.ONCE,
                    title=f"迁移: {video.title[:50]}",
                    description="从旧系统自动迁移",
                    priority=50,
                )

                schedule = await service.create_schedule(schedule_data, created_by=5)

                # 如果已经发布，更新状态
                if status == ScheduleStatus.PUBLISHED:
                    schedule.status = status
                    schedule.actual_publish_time = video.published_at or now
                    await db.commit()

                success_count += 1
                print(f"  ✓ 迁移视频 {video.id}: {video.title[:50]}")

            except Exception as e:
                failed_count += 1
                print(f"  ✗ 迁移视频 {video.id} 失败: {e}")

        print(f"\n迁移完成:")
        print(f"  成功: {success_count}")
        print(f"  失败: {failed_count}")
        print(f"  总计: {len(videos)}")


if __name__ == "__main__":
    print("=" * 60)
    print("视频定时发布数据迁移工具")
    print("=" * 60)
    print()

    asyncio.run(migrate_old_schedules())

    print()
    print("迁移完成！")
    print()
    print("注意: 旧的 video.scheduled_publish_at 字段数据未删除")
    print("建议在确认新系统正常运行后，再移除该字段")
