#!/usr/bin/env python3
"""
诊断API 500错误的脚本
直接访问数据库和缓存，检查问题根源
"""
import asyncio
import sys
from sqlalchemy import select, func
from app.database import AsyncSessionLocal
from app.models.video import Category, Country, Tag, Video
from app.models.content import Recommendation
from app.models.notification import Notification
from app.utils.cache import get_redis


async def check_database_tables():
    """检查数据库表是否存在和有数据"""
    print("=" * 80)
    print("1. 数据库表检查")
    print("=" * 80)

    async with AsyncSessionLocal() as db:
        checks = [
            ("categories", Category),
            ("countries", Country),
            ("tags", Tag),
            ("videos", Video),
            ("recommendations", Recommendation),
            ("notifications", Notification),
        ]

        for table_name, model in checks:
            try:
                result = await db.execute(select(func.count()).select_from(model))
                count = result.scalar()
                status = "✓" if count > 0 else "⚠"
                print(f"{status} {table_name:20} - {count:5} 条记录")
            except Exception as e:
                print(f"✗ {table_name:20} - 错误: {str(e)[:50]}")


async def check_cache():
    """检查Redis缓存连接"""
    print("\n" + "=" * 80)
    print("2. Redis缓存检查")
    print("=" * 80)

    try:
        redis = await get_redis()
        await redis.ping()
        print("✓ Redis连接正常")

        # 检查缓存keys
        keys = await redis.keys("*")
        print(f"✓ 缓存中有 {len(keys)} 个keys")

        # 显示一些缓存keys
        if keys:
            print("\n前10个缓存keys:")
            for key in keys[:10]:
                ttl = await redis.ttl(key)
                print(f"  - {key} (TTL: {ttl}s)")

        await redis.aclose()
    except Exception as e:
        print(f"✗ Redis连接失败: {e}")


async def test_category_query():
    """测试分类查询"""
    print("\n" + "=" * 80)
    print("3. 分类查询测试")
    print("=" * 80)

    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Category)
                .filter(Category.is_active.is_(True))
                .order_by(Category.sort_order)
            )
            categories = result.scalars().all()
            print(f"✓ 查询成功，找到 {len(categories)} 个活跃分类")

            if categories:
                print("\n前5个分类:")
                for cat in categories[:5]:
                    print(f"  - {cat.name} (id: {cat.id}, slug: {cat.slug})")

            # 测试序列化
            from app.schemas.video import CategoryResponse
            try:
                responses = [CategoryResponse.model_validate(c) for c in categories]
                print(f"✓ 序列化成功，生成 {len(responses)} 个响应对象")
            except Exception as e:
                print(f"✗ 序列化失败: {e}")

    except Exception as e:
        print(f"✗ 查询失败: {e}")
        import traceback
        traceback.print_exc()


async def test_search_dependencies():
    """测试搜索功能依赖"""
    print("\n" + "=" * 80)
    print("4. 搜索功能检查")
    print("=" * 80)

    # 检查是否配置了ElasticSearch
    from app.config import settings
    es_url = getattr(settings, 'ELASTICSEARCH_URL', None)
    if es_url:
        print(f"⚠ ElasticSearch配置: {es_url}")
    else:
        print("⚠ ElasticSearch未配置，搜索可能使用数据库全文搜索")


async def test_recommendation_system():
    """测试推荐系统"""
    print("\n" + "=" * 80)
    print("5. 推荐系统检查")
    print("=" * 80)

    try:
        async with AsyncSessionLocal() as db:
            # 检查recommendations表
            result = await db.execute(
                select(func.count()).select_from(Recommendation)
            )
            count = result.scalar()
            print(f"{'✓' if count > 0 else '⚠'} Recommendation表有 {count} 条记录")

            # 检查是否有featured视频
            from app.models.video import VideoStatus
            result = await db.execute(
                select(func.count())
                .select_from(Video)
                .filter(Video.status == VideoStatus.PUBLISHED)
                .filter(Video.is_featured.is_(True))
            )
            featured_count = result.scalar()
            print(f"{'✓' if featured_count > 0 else '⚠'} Featured视频: {featured_count} 个")

    except Exception as e:
        print(f"✗ 推荐系统检查失败: {e}")


async def test_notification_system():
    """测试通知系统"""
    print("\n" + "=" * 80)
    print("6. 通知系统检查")
    print("=" * 80)

    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(func.count()).select_from(Notification)
            )
            count = result.scalar()
            print(f"{'✓' if count >= 0 else '⚠'} Notification表有 {count} 条记录")

            # 尝试查询通知
            if count > 0:
                result = await db.execute(
                    select(Notification).limit(1)
                )
                notif = result.scalar_one_or_none()
                if notif:
                    print(f"✓ 通知对象可以正常查询")

                    # 测试序列化
                    from app.schemas.notification import NotificationResponse
                    try:
                        response = NotificationResponse.model_validate(notif)
                        print(f"✓ 通知序列化成功")
                    except Exception as e:
                        print(f"✗ 通知序列化失败: {e}")
                        import traceback
                        traceback.print_exc()

    except Exception as e:
        print(f"✗ 通知系统检查失败: {e}")
        import traceback
        traceback.print_exc()


async def test_admin_videos():
    """测试管理员视频列表"""
    print("\n" + "=" * 80)
    print("7. 管理员视频列表检查")
    print("=" * 80)

    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Video).limit(1)
            )
            video = result.scalar_one_or_none()

            if video:
                print(f"✓ 视频表有数据")

                # 检查所有关联
                print(f"  - Categories: {len(video.categories) if video.categories else 0}")
                print(f"  - Actors: {len(video.actors) if video.actors else 0}")
                print(f"  - Directors: {len(video.directors) if video.directors else 0}")
                print(f"  - Tags: {len(video.tags) if video.tags else 0}")
                print(f"  - Country: {'Yes' if video.country_id else 'No'}")

    except Exception as e:
        print(f"✗ 管理员视频检查失败: {e}")


async def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "VideoSite API 错误诊断工具" + " " * 30 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    try:
        await check_database_tables()
        await check_cache()
        await test_category_query()
        await test_search_dependencies()
        await test_recommendation_system()
        await test_notification_system()
        await test_admin_videos()

        print("\n" + "=" * 80)
        print("诊断完成")
        print("=" * 80)
        print("\n建议:")
        print("1. 检查上述标记为 ✗ 或 ⚠ 的项目")
        print("2. 如果表为空，运行数据初始化脚本")
        print("3. 检查后端日志文件获取详细错误信息")
        print("4. 清除可能损坏的缓存: redis-cli -p 6381 FLUSHDB")
        print()

    except Exception as e:
        print(f"\n诊断过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
