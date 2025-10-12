"""
深度测试数据准备脚本
创建完整的测试数据以便测试所有管理员API端点
"""
import asyncio
from datetime import datetime, timedelta

from app.database import AsyncSessionLocal
from app.models import (
    Actor,
    Announcement,
    Banner,
    Category,
    Comment,
    Country,
    Director,
    Series,
    Tag,
    User,
    Video,
)
from app.utils.security import get_password_hash


async def create_test_data():
    """创建完整的测试数据"""
    async with AsyncSessionLocal() as db:
        print("开始创建测试数据...\n")

        # 1. 创建分类
        print("1. 创建分类...")
        categories = []
        for i, name in enumerate(["动作", "喜剧", "剧情", "科幻", "恐怖"], 1):
            category = Category(
                name=name,
                slug=f"category-{i}",
                description=f"{name}类型的视频",
                is_active=True,
            )
            db.add(category)
            categories.append(category)
        await db.flush()
        print(f"   ✓ 创建了 {len(categories)} 个分类")

        # 2. 创建国家
        print("2. 创建国家/地区...")
        countries = []
        for i, (name, code) in enumerate([("中国", "CN"), ("美国", "US"), ("日本", "JP"), ("韩国", "KR")], 1):
            country = Country(
                name=name,
                code=code,
                is_active=True,
            )
            db.add(country)
            countries.append(country)
        await db.flush()
        print(f"   ✓ 创建了 {len(countries)} 个国家")

        # 3. 创建标签
        print("3. 创建标签...")
        tags = []
        for i, name in enumerate(["热血", "励志", "搞笑", "催泪", "烧脑"], 1):
            tag = Tag(
                name=name,
                slug=f"tag-{i}",
                is_active=True,
            )
            db.add(tag)
            tags.append(tag)
        await db.flush()
        print(f"   ✓ 创建了 {len(tags)} 个标签")

        # 4. 创建演员
        print("4. 创建演员...")
        actors = []
        for i, name in enumerate(["张三", "李四", "王五", "赵六"], 1):
            actor = Actor(
                name=name,
                slug=f"actor-{i}",
                bio=f"{name}是一位优秀的演员",
                is_active=True,
            )
            db.add(actor)
            actors.append(actor)
        await db.flush()
        print(f"   ✓ 创建了 {len(actors)} 个演员")

        # 5. 创建导演
        print("5. 创建导演...")
        directors = []
        for i, name in enumerate(["导演甲", "导演乙", "导演丙"], 1):
            director = Director(
                name=name,
                slug=f"director-{i}",
                bio=f"{name}是一位著名导演",
                is_active=True,
            )
            db.add(director)
            directors.append(director)
        await db.flush()
        print(f"   ✓ 创建了 {len(directors)} 个导演")

        # 6. 创建系列
        print("6. 创建系列...")
        series_list = []
        for i in range(1, 4):
            series = Series(
                name=f"测试系列{i}",
                slug=f"series-{i}",
                description=f"这是测试系列{i}",
                is_active=True,
            )
            db.add(series)
            series_list.append(series)
        await db.flush()
        print(f"   ✓ 创建了 {len(series_list)} 个系列")

        # 7. 创建用户
        print("7. 创建用户...")
        users = []
        for i in range(1, 6):
            user = User(
                email=f"user{i}@test.com",
                username=f"testuser{i}",
                hashed_password=get_password_hash("password123"),
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            users.append(user)
        await db.flush()
        print(f"   ✓ 创建了 {len(users)} 个用户")

        # 8. 创建视频
        print("8. 创建视频...")
        videos = []
        for i in range(1, 11):
            video = Video(
                title=f"测试视频{i}",
                slug=f"test-video-{i}",
                description=f"这是测试视频{i}的描述",
                duration=3600 + i * 60,
                year=2024,
                rating=7.5 + (i % 3) * 0.5,
                status="published",
                is_featured=i <= 3,
                view_count=100 * i,
                like_count=10 * i,
                category_id=categories[i % len(categories)].id,
                country_id=countries[i % len(countries)].id,
            )
            # 关联演员和导演
            video.actors = [actors[i % len(actors)]]
            video.directors = [directors[i % len(directors)]]
            video.tags = [tags[i % len(tags)]]
            if i <= 3:
                video.series_id = series_list[0].id

            db.add(video)
            videos.append(video)
        await db.flush()
        print(f"   ✓ 创建了 {len(videos)} 个视频")

        # 9. 创建评论
        print("9. 创建评论...")
        comments = []
        for i in range(1, 16):
            comment = Comment(
                content=f"这是第{i}条测试评论",
                user_id=users[i % len(users)].id,
                video_id=videos[i % len(videos)].id,
                status="approved" if i % 3 != 0 else "pending",
                like_count=i * 2,
            )
            db.add(comment)
            comments.append(comment)
        await db.flush()
        print(f"   ✓ 创建了 {len(comments)} 个评论")

        # 10. 创建横幅
        print("10. 创建横幅...")
        banners = []
        for i in range(1, 4):
            banner = Banner(
                title=f"横幅{i}",
                image_url=f"https://example.com/banner{i}.jpg",
                link_url=f"https://example.com/link{i}",
                position="home",
                sort_order=i,
                is_active=True,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(days=30),
            )
            db.add(banner)
            banners.append(banner)
        await db.flush()
        print(f"   ✓ 创建了 {len(banners)} 个横幅")

        # 11. 创建公告
        print("11. 创建公告...")
        announcements = []
        for i in range(1, 4):
            announcement = Announcement(
                title=f"公告{i}",
                content=f"这是第{i}条公告的内容",
                type="info" if i % 2 == 0 else "warning",
                is_active=True,
                sort_order=i,
            )
            db.add(announcement)
            announcements.append(announcement)
        await db.flush()
        print(f"   ✓ 创建了 {len(announcements)} 个公告")

        # 提交所有更改
        await db.commit()

        print("\n" + "=" * 60)
        print("✅ 测试数据创建完成!")
        print("=" * 60)
        print("\n数据统计:")
        print(f"  - 分类: {len(categories)}")
        print(f"  - 国家: {len(countries)}")
        print(f"  - 标签: {len(tags)}")
        print(f"  - 演员: {len(actors)}")
        print(f"  - 导演: {len(directors)}")
        print(f"  - 系列: {len(series_list)}")
        print(f"  - 用户: {len(users)}")
        print(f"  - 视频: {len(videos)}")
        print(f"  - 评论: {len(comments)}")
        print(f"  - 横幅: {len(banners)}")
        print(f"  - 公告: {len(announcements)}")
        print("\n可用于测试的ID:")
        print(f"  - 视频ID: 1-{len(videos)}")
        print(f"  - 用户ID: 1-{len(users)}")
        print(f"  - 分类ID: 1-{len(categories)}")
        print(f"  - 标签ID: 1-{len(tags)}")
        print(f"  - 演员ID: 1-{len(actors)}")
        print(f"  - 导演ID: 1-{len(directors)}")


async def check_existing_data():
    """检查现有数据"""
    async with AsyncSessionLocal() as db:
        from sqlalchemy import func, select

        print("检查现有数据...\n")

        models = [
            ("视频", Video),
            ("用户", User),
            ("分类", Category),
            ("国家", Country),
            ("标签", Tag),
            ("演员", Actor),
            ("导演", Director),
            ("系列", Series),
            ("评论", Comment),
            ("横幅", Banner),
            ("公告", Announcement),
        ]

        for name, model in models:
            result = await db.execute(select(func.count(model.id)))
            count = result.scalar()
            print(f"  {name}: {count} 条")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "check":
        asyncio.run(check_existing_data())
    else:
        asyncio.run(create_test_data())
