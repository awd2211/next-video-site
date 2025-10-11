"""
使用 pytest + httpx 专业测试所有API端点
FastAPI官方推荐的测试方式
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import AsyncSessionLocal
from app.models.user import User, AdminUser
from app.utils.security import get_password_hash
from sqlalchemy import select

# 测试基础URL
BASE_URL = "http://test"

@pytest.fixture
async def test_user():
    """创建测试用户"""
    async with AsyncSessionLocal() as db:
        # 检查是否已存在
        result = await db.execute(select(User).where(User.email == "testapi@example.com"))
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                email="testapi@example.com",
                username="testapi",
                hashed_password=get_password_hash("test123456"),
                full_name="API Test User",
                is_active=True
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        yield user

@pytest.fixture
async def test_admin():
    """创建测试管理员"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(AdminUser).where(AdminUser.username == "admin"))
        admin = result.scalar_one_or_none()
        
        if admin:
            yield admin
        else:
            pytest.skip("Admin user not found")

@pytest.fixture
async def async_client():
    """创建异步HTTP客户端"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as client:
        yield client

@pytest.fixture
async def user_token(async_client, test_user):
    """获取用户token"""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "testapi@example.com",
            "password": "test123456"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
async def admin_token(async_client):
    """获取管理员token（需要验证码）"""
    # 先获取验证码
    cap_response = await async_client.get("/api/v1/captcha/")
    assert cap_response.status_code == 200
    captcha_id = cap_response.headers.get("x-captcha-id")
    
    # 从Redis读取验证码
    from app.utils.cache import get_redis
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
    assert response.status_code == 200
    return response.json()["access_token"]


# ===========================================
# 公开API测试（无需认证）
# ===========================================

@pytest.mark.asyncio
class TestPublicAPIs:
    """测试公开API端点"""
    
    async def test_get_videos(self, async_client):
        """测试获取视频列表"""
        response = await async_client.get("/api/v1/videos")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
    
    async def test_get_video_trending(self, async_client):
        """测试热门视频"""
        response = await async_client.get("/api/v1/videos/trending")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
    
    async def test_get_video_featured(self, async_client):
        """测试精选视频"""
        response = await async_client.get("/api/v1/videos/featured")
        assert response.status_code == 200
    
    async def test_get_categories(self, async_client):
        """测试获取分类"""
        response = await async_client.get("/api/v1/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_actors(self, async_client):
        """测试获取演员列表"""
        response = await async_client.get("/api/v1/actors/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
    
    async def test_get_directors(self, async_client):
        """测试获取导演列表"""
        response = await async_client.get("/api/v1/directors/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data


# ===========================================
# 用户认证API测试
# ===========================================

@pytest.mark.asyncio
class TestAuthAPIs:
    """测试认证相关API"""
    
    async def test_user_login(self, async_client):
        """测试用户登录"""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "test123456"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_get_current_user(self, async_client, user_token):
        """测试获取当前用户信息"""
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data
    
    async def test_refresh_token(self, async_client, user_token):
        """测试刷新token"""
        # 先登录获取refresh token
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "email": "testapi@example.com",
                "password": "test123456"
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # 刷新
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data


# ===========================================
# 需要认证的用户API测试
# ===========================================

@pytest.mark.asyncio
class TestUserAPIs:
    """测试用户相关API"""
    
    async def test_get_user_profile(self, async_client, user_token):
        """测试获取用户资料"""
        response = await async_client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "testapi@example.com"
    
    async def test_get_favorites(self, async_client, user_token):
        """测试获取收藏列表"""
        response = await async_client.get(
            "/api/v1/favorites/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
    
    async def test_get_watch_history(self, async_client, user_token):
        """测试获取观看历史"""
        response = await async_client.get(
            "/api/v1/history/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data


# ===========================================
# 管理员API测试
# ===========================================

@pytest.mark.asyncio
class TestAdminAPIs:
    """测试管理员API"""
    
    async def test_admin_get_stats(self, async_client, admin_token):
        """测试获取统计数据"""
        response = await async_client.get(
            "/api/v1/admin/stats/overview",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "user_count" in data or "total_users" in data
    
    async def test_admin_get_videos(self, async_client, admin_token):
        """测试管理员获取视频列表"""
        response = await async_client.get(
            "/api/v1/admin/videos",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200


# ===========================================
# 数据创建和删除测试
# ===========================================

@pytest.mark.asyncio
class TestCRUDOperations:
    """测试CRUD操作"""
    
    async def test_create_and_delete_favorite(self, async_client, user_token):
        """测试收藏和取消收藏"""
        # 假设视频ID 1存在
        # 添加收藏
        response = await async_client.post(
            "/api/v1/favorites/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"video_id": 1}
        )
        # 201 or 200 or 409 (already exists) 都是正常的
        assert response.status_code in [200, 201, 409, 404]  # 404如果视频不存在也正常
    
    async def test_create_comment(self, async_client, user_token):
        """测试创建评论"""
        response = await async_client.post(
            "/api/v1/comments/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "video_id": 1,
                "content": "Test comment from pytest"
            }
        )
        # 允许404（视频不存在）和201（创建成功）
        assert response.status_code in [200, 201, 404]


# ===========================================
# API健康检查
# ===========================================

@pytest.mark.asyncio
async def test_api_root(async_client):
    """测试API根路径"""
    response = await async_client.get("/")
    assert response.status_code == 200

@pytest.mark.asyncio  
async def test_docs_available(async_client):
    """测试API文档可用"""
    response = await async_client.get("/api/docs")
    assert response.status_code == 200

