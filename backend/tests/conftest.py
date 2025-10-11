"""
Pytest配置和共享fixtures
"""
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from typing import AsyncGenerator

from app.main import app
from app.database import AsyncSessionLocal
from app.models.user import User, AdminUser
from app.models.video import Video, Category, Country, Tag
from app.utils.security import get_password_hash


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """创建异步HTTP客户端"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def test_user() -> User:
    """创建测试用户"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.email == "pytest@example.com")
        )
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                email="pytest@example.com",
                username="pytest_user",
                hashed_password=get_password_hash("test123456"),
                full_name="Pytest Test User",
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        return user


@pytest.fixture
async def test_admin() -> AdminUser:
    """获取测试管理员"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(AdminUser).where(AdminUser.username == "admin")
        )
        admin = result.scalar_one_or_none()
        
        if not admin:
            pytest.fail("Admin user not found. Run: python scripts/init_data.py")
        
        return admin


@pytest.fixture
async def user_token(async_client: AsyncClient, test_user: User) -> str:
    """获取用户access token"""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "pytest@example.com",
            "password": "test123456"
        }
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture
async def admin_token(async_client: AsyncClient) -> str:
    """获取管理员access token"""
    # 获取验证码
    from app.utils.cache import get_redis
    
    cap_response = await async_client.get("/api/v1/captcha/")
    assert cap_response.status_code == 200
    captcha_id = cap_response.headers.get("x-captcha-id")
    
    # 从Redis读取验证码
    redis = await get_redis()
    captcha_code = await redis.get(f"captcha:{captcha_id}")
    await redis.aclose()
    
    # 登录
    response = await async_client.post(
        "/api/v1/auth/admin/login",
        json={
            "username": "admin",
            "password": "admin123456",
            "captcha_id": captcha_id,
            "captcha_code": captcha_code
        }
    )
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture
async def test_video() -> Video:
    """创建测试视频"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Video).where(Video.slug == "pytest-test-video")
        )
        video = result.scalar_one_or_none()
        
        if not video:
            from app.models.video import VideoType, VideoStatus
            video = Video(
                title="Pytest Test Video",
                slug="pytest-test-video",
                description="Test video for pytest",
                video_type=VideoType.MOVIE,
                status=VideoStatus.PUBLISHED,
                video_url="https://example.com/test.mp4",
                duration=120,
                view_count=100,
                like_count=10,
                favorite_count=5,
                comment_count=3,
                average_rating=8.5,
                rating_count=20,
            )
            db.add(video)
            await db.commit()
            await db.refresh(video)
        
        return video


@pytest.fixture
async def test_category() -> Category:
    """创建测试分类"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Category).where(Category.slug == "pytest-test")
        )
        category = result.scalar_one_or_none()
        
        if not category:
            category = Category(
                name="Pytest Test",
                slug="pytest-test",
                description="Test category",
                is_active=True,
            )
            db.add(category)
            await db.commit()
            await db.refresh(category)
        
        return category

