"""
缓存预热工具
在系统启动或定时任务时预加载热门数据到缓存
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.models.video import Video, Category, Country, Tag, VideoStatus
from app.schemas.video import VideoListResponse, CategoryResponse, CountryResponse, TagResponse
from app.utils.cache import Cache
from app.database import async_session_maker
import asyncio


class CacheWarmer:
    """缓存预热类"""

    @staticmethod
    async def warm_categories():
        """预热分类数据"""
        print("Warming up categories cache...")
        async with async_session_maker() as db:
            result = await db.execute(
                select(Category).filter(Category.is_active == True).order_by(Category.sort_order)
            )
            categories = result.scalars().all()
            response = [CategoryResponse.model_validate(c) for c in categories]
            await Cache.set("categories:all:active", response, ttl=1800)
            print(f"Cached {len(categories)} categories")

    @staticmethod
    async def warm_countries():
        """预热国家数据"""
        print("Warming up countries cache...")
        async with async_session_maker() as db:
            result = await db.execute(select(Country).order_by(Country.name))
            countries = result.scalars().all()
            response = [CountryResponse.model_validate(c) for c in countries]
            await Cache.set("countries:all", response, ttl=3600)
            print(f"Cached {len(countries)} countries")

    @staticmethod
    async def warm_tags():
        """预热标签数据"""
        print("Warming up tags cache...")
        async with async_session_maker() as db:
            result = await db.execute(select(Tag).order_by(Tag.name))
            tags = result.scalars().all()
            response = [TagResponse.model_validate(c) for c in tags]
            await Cache.set("tags:all", response, ttl=1800)
            print(f"Cached {len(tags)} tags")

    @staticmethod
    async def warm_trending_videos(page_size: int = 20):
        """预热热门视频数据"""
        print("Warming up trending videos cache...")
        async with async_session_maker() as db:
            # 预热前3页
            for page in range(1, 4):
                query = select(Video).options(
                    selectinload(Video.country)
                ).filter(Video.status == VideoStatus.PUBLISHED).order_by(desc(Video.view_count))

                # Paginate
                offset = (page - 1) * page_size
                query = query.offset(offset).limit(page_size)

                result = await db.execute(query)
                videos = result.scalars().all()

                response = {
                    "total": 0,  # Will be updated on first real request
                    "page": page,
                    "page_size": page_size,
                    "items": [VideoListResponse.model_validate(v) for v in videos],
                }

                cache_key = f"trending_videos:page_{page}:size_{page_size}"
                await Cache.set(cache_key, response, ttl=600)
                print(f"Cached trending videos page {page}")

    @staticmethod
    async def warm_featured_videos(page_size: int = 20):
        """预热推荐视频数据"""
        print("Warming up featured videos cache...")
        async with async_session_maker() as db:
            # 预热前2页
            for page in range(1, 3):
                query = select(Video).options(
                    selectinload(Video.country)
                ).filter(
                    Video.status == VideoStatus.PUBLISHED,
                    Video.is_featured == True
                ).order_by(desc(Video.sort_order), desc(Video.created_at))

                # Paginate
                offset = (page - 1) * page_size
                query = query.offset(offset).limit(page_size)

                result = await db.execute(query)
                videos = result.scalars().all()

                response = {
                    "total": 0,  # Will be updated on first real request
                    "page": page,
                    "page_size": page_size,
                    "items": [VideoListResponse.model_validate(v) for v in videos],
                }

                cache_key = f"featured_videos:page_{page}:size_{page_size}"
                await Cache.set(cache_key, response, ttl=900)
                print(f"Cached featured videos page {page}")

    @staticmethod
    async def warm_recommended_videos(page_size: int = 20):
        """预热推荐视频数据"""
        print("Warming up recommended videos cache...")
        async with async_session_maker() as db:
            # 预热前2页
            for page in range(1, 3):
                query = select(Video).options(
                    selectinload(Video.country)
                ).filter(
                    Video.status == VideoStatus.PUBLISHED,
                    Video.is_recommended == True
                ).order_by(desc(Video.sort_order), desc(Video.created_at))

                # Paginate
                offset = (page - 1) * page_size
                query = query.offset(offset).limit(page_size)

                result = await db.execute(query)
                videos = result.scalars().all()

                response = {
                    "total": 0,  # Will be updated on first real request
                    "page": page,
                    "page_size": page_size,
                    "items": [VideoListResponse.model_validate(v) for v in videos],
                }

                cache_key = f"recommended_videos:page_{page}:size_{page_size}"
                await Cache.set(cache_key, response, ttl=900)
                print(f"Cached recommended videos page {page}")

    @staticmethod
    async def warm_all():
        """预热所有数据"""
        print("Starting cache warming process...")
        start_time = asyncio.get_event_loop().time()

        try:
            # 并行预热
            await asyncio.gather(
                CacheWarmer.warm_categories(),
                CacheWarmer.warm_countries(),
                CacheWarmer.warm_tags(),
                CacheWarmer.warm_trending_videos(),
                CacheWarmer.warm_featured_videos(),
                CacheWarmer.warm_recommended_videos(),
            )

            elapsed = asyncio.get_event_loop().time() - start_time
            print(f"Cache warming completed in {elapsed:.2f} seconds")
        except Exception as e:
            print(f"Error during cache warming: {e}")
            raise


async def run_cache_warmer():
    """运行缓存预热（可用于定时任务）"""
    await CacheWarmer.warm_all()


if __name__ == "__main__":
    # 直接运行此脚本进行缓存预热
    asyncio.run(run_cache_warmer())
