"""
数据库种子数据脚本
用于生成测试数据
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import random

from app.database import async_session_maker
from app.models.video import Video, Category, Country, Tag, Actor, Director, VideoStatus, VideoType
from app.models.series import Series, SeriesType, SeriesStatus
from app.utils.security import get_password_hash


# 测试数据
CATEGORIES = [
    {"name": "动作", "slug": "action", "description": "刺激的动作场面"},
    {"name": "喜剧", "slug": "comedy", "description": "轻松搞笑"},
    {"name": "剧情", "slug": "drama", "description": "深刻的故事"},
    {"name": "科幻", "slug": "sci-fi", "description": "未来与科技"},
    {"name": "恐怖", "slug": "horror", "description": "惊悚恐怖"},
    {"name": "爱情", "slug": "romance", "description": "浪漫爱情"},
    {"name": "动画", "slug": "animation", "description": "动画作品"},
    {"name": "纪录片", "slug": "documentary", "description": "真实记录"},
]

COUNTRIES = [
    {"name": "美国", "code": "US"},
    {"name": "中国", "code": "CN"},
    {"name": "日本", "code": "JP"},
    {"name": "韩国", "code": "KR"},
    {"name": "英国", "code": "GB"},
    {"name": "法国", "code": "FR"},
]

TAGS = [
    {"name": "高分", "slug": "high-rated"},
    {"name": "经典", "slug": "classic"},
    {"name": "热门", "slug": "trending"},
    {"name": "新片", "slug": "new-release"},
    {"name": "独家", "slug": "exclusive"},
    {"name": "4K", "slug": "4k"},
    {"name": "杜比", "slug": "dolby"},
]

ACTORS = [
    {"name": "汤姆·克鲁斯", "avatar": None},
    {"name": "莱昂纳多·迪卡普里奥", "avatar": None},
    {"name": "斯嘉丽·约翰逊", "avatar": None},
    {"name": "罗伯特·唐尼", "avatar": None},
    {"name": "安吉丽娜·朱莉", "avatar": None},
    {"name": "成龙", "avatar": None},
    {"name": "周星驰", "avatar": None},
    {"name": "章子怡", "avatar": None},
]

DIRECTORS = [
    {"name": "克里斯托弗·诺兰", "avatar": None},
    {"name": "史蒂文·斯皮尔伯格", "avatar": None},
    {"name": "昆汀·塔伦蒂诺", "avatar": None},
    {"name": "张艺谋", "avatar": None},
    {"name": "宫崎骏", "avatar": None},
    {"name": "詹姆斯·卡梅隆", "avatar": None},
]

VIDEO_TITLES = [
    "星际穿越", "盗梦空间", "肖申克的救赎", "阿甘正传", "泰坦尼克号",
    "复仇者联盟", "蝙蝠侠：黑暗骑士", "教父", "低俗小说", "搏击俱乐部",
    "黑客帝国", "指环王", "哈利·波特", "星球大战", "侏罗纪公园",
    "功夫", "大话西游", "让子弹飞", "无间道", "英雄",
    "千与千寻", "你的名字", "天气之子", "进击的巨人", "火影忍者",
    "寄生虫", "釜山行", "太极旗飘扬", "老男孩", "杀人回忆"
]

VIDEO_DESCRIPTIONS = [
    "一部震撼人心的科幻巨作，探索时间与空间的奥秘。",
    "精彩的动作场面，扣人心弦的剧情发展。",
    "感人至深的故事，让人回味无穷。",
    "视觉效果惊艳，特效制作精良。",
    "深刻的人性探讨，引人深思。",
    "轻松幽默，充满欢笑。",
    "紧张刺激，全程无尿点。",
    "经典之作，值得反复观看。",
]


async def create_categories(session: AsyncSession):
    """创建分类"""
    print("创建分类...")
    categories = []
    for cat_data in CATEGORIES:
        # 检查是否已存在
        result = await session.execute(
            select(Category).filter(Category.slug == cat_data["slug"])
        )
        existing = result.scalar_one_or_none()
        if not existing:
            category = Category(**cat_data)
            session.add(category)
            categories.append(category)
        else:
            categories.append(existing)

    await session.commit()
    print(f"✓ 创建了 {len(categories)} 个分类")
    return categories


async def create_countries(session: AsyncSession):
    """创建国家/地区"""
    print("创建国家/地区...")
    countries = []
    for country_data in COUNTRIES:
        result = await session.execute(
            select(Country).filter(Country.code == country_data["code"])
        )
        existing = result.scalar_one_or_none()
        if not existing:
            country = Country(**country_data)
            session.add(country)
            countries.append(country)
        else:
            countries.append(existing)

    await session.commit()
    print(f"✓ 创建了 {len(countries)} 个国家/地区")
    return countries


async def create_tags(session: AsyncSession):
    """创建标签"""
    print("创建标签...")
    tags = []
    for tag_data in TAGS:
        result = await session.execute(
            select(Tag).filter(Tag.slug == tag_data["slug"])
        )
        existing = result.scalar_one_or_none()
        if not existing:
            tag = Tag(**tag_data)
            session.add(tag)
            tags.append(tag)
        else:
            tags.append(existing)

    await session.commit()
    print(f"✓ 创建了 {len(tags)} 个标签")
    return tags


async def create_actors(session: AsyncSession):
    """创建演员"""
    print("创建演员...")
    actors = []
    for actor_data in ACTORS:
        result = await session.execute(
            select(Actor).filter(Actor.name == actor_data["name"])
        )
        existing = result.scalar_one_or_none()
        if not existing:
            actor = Actor(**actor_data)
            session.add(actor)
            actors.append(actor)
        else:
            actors.append(existing)

    await session.commit()
    print(f"✓ 创建了 {len(actors)} 个演员")
    return actors


async def create_directors(session: AsyncSession):
    """创建导演"""
    print("创建导演...")
    directors = []
    for director_data in DIRECTORS:
        result = await session.execute(
            select(Director).filter(Director.name == director_data["name"])
        )
        existing = result.scalar_one_or_none()
        if not existing:
            director = Director(**director_data)
            session.add(director)
            directors.append(director)
        else:
            directors.append(existing)

    await session.commit()
    print(f"✓ 创建了 {len(directors)} 个导演")
    return directors


async def create_videos(session: AsyncSession, categories, countries, tags, actors, directors, count=50):
    """创建视频"""
    print(f"创建 {count} 个视频...")
    videos = []

    video_types = [VideoType.MOVIE, VideoType.TV_SERIES, VideoType.ANIME, VideoType.DOCUMENTARY]

    for i in range(count):
        title = random.choice(VIDEO_TITLES) + f" {i+1}"

        video = Video(
            title=title,
            slug=f"video-{i+1}",
            description=random.choice(VIDEO_DESCRIPTIONS),
            video_type=random.choice(video_types),
            status=VideoStatus.PUBLISHED,
            poster_url=f"https://picsum.photos/seed/{i+1}/400/600",
            backdrop_url=f"https://picsum.photos/seed/{i+1}/1200/675",
            video_url=f"https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/720/Big_Buck_Bunny_720_10s_1MB.mp4",
            release_year=random.randint(2015, 2024),
            release_date=datetime.now() - timedelta(days=random.randint(0, 365*5)),
            duration=random.randint(90, 180),  # 90-180 minutes
            country_id=random.choice(countries).id,
            language=random.choice(["中文", "英语", "日语", "韩语"]),
            average_rating=round(random.uniform(6.0, 9.5), 1),
            view_count=random.randint(1000, 1000000),
            like_count=random.randint(100, 50000),
            favorite_count=random.randint(50, 20000),
            comment_count=random.randint(10, 5000),
            rating_count=random.randint(100, 10000),
            is_featured=random.choice([True, False, False, False]),  # 25% featured
            is_recommended=random.choice([True, False, False]),  # 33% recommended
            is_av1_available=random.choice([True, False]),  # 50% AV1
            published_at=datetime.now() - timedelta(days=random.randint(0, 365)),
        )

        session.add(video)
        videos.append(video)

    await session.flush()  # Flush to get IDs

    # Add relationships using association objects
    print("添加视频关联...")
    from app.models.video import VideoCategory, VideoTag, VideoActor, VideoDirector

    for video in videos:
        # Categories (1-3 per video)
        video_categories = random.sample(categories, k=random.randint(1, 3))
        for category in video_categories:
            vc = VideoCategory(video_id=video.id, category_id=category.id)
            session.add(vc)

        # Tags (0-3 per video)
        video_tags = random.sample(tags, k=random.randint(0, 3))
        for tag in video_tags:
            vt = VideoTag(video_id=video.id, tag_id=tag.id)
            session.add(vt)

        # Actors (2-5 per video)
        video_actors = random.sample(actors, k=random.randint(2, min(5, len(actors))))
        for actor in video_actors:
            va = VideoActor(
                video_id=video.id,
                actor_id=actor.id,
                role_name=random.choice(["主角", "配角", "客串", "特邀出演"])
            )
            session.add(va)

        # Directors (1-2 per video)
        video_directors = random.sample(directors, k=random.randint(1, min(2, len(directors))))
        for director in video_directors:
            vd = VideoDirector(video_id=video.id, director_id=director.id)
            session.add(vd)

    await session.commit()
    print(f"✓ 创建了 {len(videos)} 个视频")
    return videos


async def create_series(session: AsyncSession, videos, count=5):
    """创建系列/专辑"""
    print(f"创建 {count} 个系列...")
    series_list = []

    series_titles = [
        "漫威电影宇宙系列",
        "哈利·波特系列",
        "指环王三部曲",
        "星球大战系列",
        "DC超级英雄系列",
    ]

    for i in range(count):
        series = Series(
            title=series_titles[i] if i < len(series_titles) else f"系列 {i+1}",
            description=f"这是一个精彩的系列作品，包含多部相关影片。",
            cover_image=f"https://picsum.photos/seed/series-{i+1}/800/450",
            type=SeriesType.SERIES,
            status=SeriesStatus.PUBLISHED,
            display_order=i,
            is_featured=i < 2,  # First 2 are featured
        )
        session.add(series)
        await session.flush()

        # Add 3-8 videos to each series using INSERT
        from app.models.series import series_videos as series_videos_table
        selected_videos = random.sample(videos, k=random.randint(3, min(8, len(videos))))
        for idx, video in enumerate(selected_videos, 1):
            await session.execute(
                series_videos_table.insert().values(
                    series_id=series.id,
                    video_id=video.id,
                    episode_number=idx
                )
            )

        series.total_episodes = len(selected_videos)
        series_list.append(series)

    await session.commit()
    print(f"✓ 创建了 {len(series_list)} 个系列")
    return series_list


async def clean_existing_data(session: AsyncSession):
    """清除现有测试数据"""
    print("清除现有数据...")
    try:
        # Delete in reverse order of dependencies
        await session.execute(text("DELETE FROM series_videos"))
        await session.execute(text("DELETE FROM video_categories"))
        await session.execute(text("DELETE FROM video_tags"))
        await session.execute(text("DELETE FROM video_actors"))
        await session.execute(text("DELETE FROM video_directors"))
        await session.execute(text("DELETE FROM series"))
        await session.execute(text("DELETE FROM videos"))
        await session.execute(text("DELETE FROM categories"))
        await session.execute(text("DELETE FROM countries"))
        await session.execute(text("DELETE FROM tags"))
        await session.execute(text("DELETE FROM actors"))
        await session.execute(text("DELETE FROM directors"))
        await session.commit()
        print("✓ 现有数据已清除")
    except Exception as e:
        print(f"⚠️  清除数据时出错 (可能是首次运行): {e}")
        await session.rollback()


async def main():
    """主函数"""
    print("=" * 60)
    print("开始生成测试数据...")
    print("=" * 60)

    async with async_session_maker() as session:
        try:
            # Clean existing data first
            await clean_existing_data(session)

            # Create base data
            categories = await create_categories(session)
            countries = await create_countries(session)
            tags = await create_tags(session)
            actors = await create_actors(session)
            directors = await create_directors(session)

            # Create videos
            videos = await create_videos(
                session,
                categories,
                countries,
                tags,
                actors,
                directors,
                count=50  # 创建50个视频
            )

            # Create series
            series = await create_series(session, videos, count=5)

            print("\n" + "=" * 60)
            print("✅ 测试数据生成完成！")
            print("=" * 60)
            print(f"分类: {len(categories)} 个")
            print(f"国家: {len(countries)} 个")
            print(f"标签: {len(tags)} 个")
            print(f"演员: {len(actors)} 个")
            print(f"导演: {len(directors)} 个")
            print(f"视频: {len(videos)} 个")
            print(f"系列: {len(series)} 个")
            print("=" * 60)

        except Exception as e:
            print(f"❌ 错误: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
