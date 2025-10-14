"""
测试视频相关模型
包括: Video, Category, Country, Tag, Actor, Director
"""
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.video import Video, Category, Country, Tag, Actor, Director, VideoType, VideoStatus
from app.database import AsyncSessionLocal


@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestVideoModel:
    """Video 模型测试"""

    async def test_create_video(self):
        """测试创建视频"""
        async with AsyncSessionLocal() as db:
            video = Video(
                title="Test Video Model",
                slug="test-video-model-unique",
                video_type=VideoType.MOVIE,
                status=VideoStatus.DRAFT
            )
            db.add(video)
            await db.commit()
            await db.refresh(video)
            
            assert video.id is not None
            assert video.title == "Test Video Model"
            assert video.video_type == VideoType.MOVIE
            assert video.status == VideoStatus.DRAFT
            
            await db.delete(video)
            await db.commit()

    async def test_video_unique_slug(self):
        """测试视频 slug 唯一性"""
        async with AsyncSessionLocal() as db:
            video1 = Video(
                title="Video 1",
                slug="unique-slug-test",
                video_type=VideoType.MOVIE,
                status=VideoStatus.DRAFT
            )
            db.add(video1)
            await db.commit()
            
            video2 = Video(
                title="Video 2",
                slug="unique-slug-test",
                video_type=VideoType.MOVIE,
                status=VideoStatus.DRAFT
            )
            db.add(video2)
            
            with pytest.raises(IntegrityError):
                await db.commit()
            
            await db.rollback()
            await db.delete(video1)
            await db.commit()

    async def test_video_default_values(self):
        """测试视频默认值"""
        async with AsyncSessionLocal() as db:
            video = Video(
                title="Defaults Test",
                slug="defaults-test-unique",
                video_type=VideoType.MOVIE,
                status=VideoStatus.DRAFT
            )
            db.add(video)
            await db.commit()
            await db.refresh(video)
            
            assert video.view_count == 0
            assert video.like_count == 0
            assert video.favorite_count == 0
            assert video.comment_count == 0
            assert video.is_featured is False
            assert video.created_at is not None
            
            await db.delete(video)
            await db.commit()

    async def test_video_with_country(self):
        """测试视频关联国家"""
        async with AsyncSessionLocal() as db:
            # 查找或创建国家
            result = await db.execute(select(Country).where(Country.code == "US"))
            country = result.scalar_one_or_none()
            
            if not country:
                country = Country(name="美国", code="US")
                db.add(country)
                await db.commit()
                await db.refresh(country)
            
            video = Video(
                title="Video with Country",
                slug="video-country-test-unique",
                video_type=VideoType.MOVIE,
                status=VideoStatus.DRAFT,
                country_id=country.id
            )
            db.add(video)
            await db.commit()
            await db.refresh(video)
            
            assert video.country_id == country.id
            
            await db.delete(video)
            await db.commit()


@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestCategoryModel:
    """Category 模型测试"""

    async def test_create_category(self):
        """测试创建分类"""
        async with AsyncSessionLocal() as db:
            category = Category(
                name="测试分类",
                slug="test-category-unique",
                description="测试描述"
            )
            db.add(category)
            await db.commit()
            await db.refresh(category)
            
            assert category.id is not None
            assert category.name == "测试分类"
            assert category.is_active is True
            
            await db.delete(category)
            await db.commit()

    async def test_category_unique_slug(self):
        """测试分类 slug 唯一性"""
        async with AsyncSessionLocal() as db:
            cat1 = Category(name="分类1", slug="unique-cat-slug")
            db.add(cat1)
            await db.commit()
            
            cat2 = Category(name="分类2", slug="unique-cat-slug")
            db.add(cat2)
            
            with pytest.raises(IntegrityError):
                await db.commit()
            
            await db.rollback()
            await db.delete(cat1)
            await db.commit()

    async def test_category_parent_child(self):
        """测试分类父子关系"""
        async with AsyncSessionLocal() as db:
            parent = Category(name="父分类", slug="parent-cat-unique")
            db.add(parent)
            await db.commit()
            await db.refresh(parent)
            
            child = Category(
                name="子分类",
                slug="child-cat-unique",
                parent_id=parent.id
            )
            db.add(child)
            await db.commit()
            await db.refresh(child)
            
            assert child.parent_id == parent.id
            
            await db.delete(child)
            await db.delete(parent)
            await db.commit()


@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestCountryModel:
    """Country 模型测试"""

    async def test_create_country(self):
        """测试创建国家"""
        async with AsyncSessionLocal() as db:
            country = Country(
                name="测试国家",
                code="TC"
            )
            db.add(country)
            await db.commit()
            await db.refresh(country)
            
            assert country.id is not None
            assert country.code == "TC"
            
            await db.delete(country)
            await db.commit()

    async def test_country_unique_code(self):
        """测试国家代码唯一性"""
        async with AsyncSessionLocal() as db:
            country1 = Country(name="国家1", code="C1")
            db.add(country1)
            await db.commit()
            
            country2 = Country(name="国家2", code="C1")
            db.add(country2)
            
            with pytest.raises(IntegrityError):
                await db.commit()
            
            await db.rollback()
            await db.delete(country1)
            await db.commit()


@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestTagModel:
    """Tag 模型测试"""

    async def test_create_tag(self):
        """测试创建标签"""
        async with AsyncSessionLocal() as db:
            tag = Tag(
                name="测试标签",
                slug="test-tag-unique"
            )
            db.add(tag)
            await db.commit()
            await db.refresh(tag)
            
            assert tag.id is not None
            assert tag.name == "测试标签"
            
            await db.delete(tag)
            await db.commit()


@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestActorModel:
    """Actor 模型测试"""

    async def test_create_actor(self):
        """测试创建演员"""
        async with AsyncSessionLocal() as db:
            actor = Actor(
                name="测试演员",
                biography="演员简介"
            )
            db.add(actor)
            await db.commit()
            await db.refresh(actor)
            
            assert actor.id is not None
            assert actor.name == "测试演员"
            
            await db.delete(actor)
            await db.commit()


@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestDirectorModel:
    """Director 模型测试"""

    async def test_create_director(self):
        """测试创建导演"""
        async with AsyncSessionLocal() as db:
            director = Director(
                name="测试导演",
                biography="导演简介"
            )
            db.add(director)
            await db.commit()
            await db.refresh(director)
            
            assert director.id is not None
            assert director.name == "测试导演"
            
            await db.delete(director)
            await db.commit()

