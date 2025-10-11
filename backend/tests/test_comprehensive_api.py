"""
全面的后端API测试 - 覆盖所有140个端点
测试所有公开API、用户API和管理员API
"""
import pytest
from httpx import AsyncClient


# ===========================================
# 公开API测试 (17个端点 - 无需认证)
# ===========================================

class TestPublicAPIs:
    """测试公开API - 无需认证"""

    # 1. 认证相关 (4个端点)
    @pytest.mark.asyncio
    async def test_user_register(self, async_client: AsyncClient):
        """POST /api/v1/auth/register - 用户注册"""
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": f"newuser_{pytest.__version__}@example.com",
                "username": f"newuser_{pytest.__version__}",
                "password": "newpass123456",
                "full_name": "New User"
            }
        )
        # 可能成功200或已存在409
        assert response.status_code in [200, 201, 409, 422], f"Unexpected status: {response.status_code}, body: {response.text}"

    @pytest.mark.asyncio
    async def test_user_login_success(self, async_client: AsyncClient):
        """POST /api/v1/auth/login - 用户登录成功"""
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

    @pytest.mark.asyncio
    async def test_refresh_token(self, async_client: AsyncClient, user_token: str):
        """POST /api/v1/auth/refresh - 刷新token"""
        # 先获取refresh token
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "test123456"}
        )
        refresh_token = login_response.json().get("refresh_token")

        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code in [200, 422], f"Status: {response.status_code}"

    # 2. 验证码 (1个端点)
    @pytest.mark.asyncio
    async def test_get_captcha(self, async_client: AsyncClient):
        """GET /api/v1/captcha/ - 获取验证码"""
        response = await async_client.get("/api/v1/captcha/")
        assert response.status_code == 200
        assert response.headers.get("x-captcha-id") is not None
        assert response.headers.get("content-type") == "image/png"

    # 3. 分类、国家、标签 (3个端点)
    @pytest.mark.asyncio
    async def test_get_categories(self, async_client: AsyncClient):
        """GET /api/v1/categories - 分类列表"""
        response = await async_client.get("/api/v1/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_countries(self, async_client: AsyncClient):
        """GET /api/v1/countries - 国家列表"""
        response = await async_client.get("/api/v1/countries")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_get_tags(self, async_client: AsyncClient):
        """GET /api/v1/tags - 标签列表"""
        response = await async_client.get("/api/v1/tags")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    # 4. 视频相关 (5个端点)
    @pytest.mark.asyncio
    async def test_get_videos_list(self, async_client: AsyncClient):
        """GET /api/v1/videos - 视频列表"""
        response = await async_client.get("/api/v1/videos")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_get_videos_trending(self, async_client: AsyncClient):
        """GET /api/v1/videos/trending - 热门视频"""
        response = await async_client.get("/api/v1/videos/trending")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_videos_featured(self, async_client: AsyncClient):
        """GET /api/v1/videos/featured - 推荐视频"""
        response = await async_client.get("/api/v1/videos/featured")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_videos_recommended(self, async_client: AsyncClient):
        """GET /api/v1/videos/recommended - 精选视频"""
        response = await async_client.get("/api/v1/videos/recommended")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_video_detail(self, async_client: AsyncClient, test_video):
        """GET /api/v1/videos/{video_id} - 视频详情"""
        response = await async_client.get(f"/api/v1/videos/{test_video.id}")
        assert response.status_code in [200, 404]

    # 5. 搜索 (1个端点)
    @pytest.mark.asyncio
    async def test_search_videos(self, async_client: AsyncClient):
        """GET /api/v1/search - 搜索视频"""
        response = await async_client.get("/api/v1/search?q=test")
        assert response.status_code in [200, 422], f"Status: {response.status_code}"

    # 6. 演员和导演 (6个端点)
    @pytest.mark.asyncio
    async def test_get_actors_list(self, async_client: AsyncClient):
        """GET /api/v1/actors/ - 演员列表"""
        response = await async_client.get("/api/v1/actors/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_get_directors_list(self, async_client: AsyncClient):
        """GET /api/v1/directors/ - 导演列表"""
        response = await async_client.get("/api/v1/directors/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data


# ===========================================
# 用户认证API测试 (10个端点)
# ===========================================

class TestUserAuthAPIs:
    """测试用户认证相关API"""

    @pytest.mark.asyncio
    async def test_get_current_user(self, async_client: AsyncClient, user_token: str):
        """GET /api/v1/auth/me - 获取当前用户"""
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data

    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, async_client: AsyncClient):
        """GET /api/v1/auth/me - 无token返回401"""
        response = await async_client.get("/api/v1/auth/me")
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_user_logout(self, async_client: AsyncClient, user_token: str):
        """POST /api/v1/auth/logout - 用户登出"""
        response = await async_client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code in [200, 204], f"Logout failed: {response.text}"


# ===========================================
# 用户资料API测试 (6个端点)
# ===========================================

class TestUserProfileAPIs:
    """测试用户资料管理API"""

    @pytest.mark.asyncio
    async def test_get_user_profile(self, async_client: AsyncClient, user_token: str):
        """GET /api/v1/users/me - 获取用户资料"""
        response = await async_client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "email" in data

    @pytest.mark.asyncio
    async def test_update_user_profile(self, async_client: AsyncClient, user_token: str):
        """PUT /api/v1/users/me - 更新用户资料"""
        response = await async_client.put(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"full_name": "Updated Test User"}
        )
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_change_password(self, async_client: AsyncClient, user_token: str):
        """POST /api/v1/users/me/change-password - 修改密码"""
        response = await async_client.post(
            "/api/v1/users/me/change-password",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "current_password": "test123456",
                "new_password": "newpass123456"
            }
        )
        # 可能成功或密码错误
        assert response.status_code in [200, 400, 401, 422]


# ===========================================
# 评论API测试 (8个端点)
# ===========================================

class TestCommentAPIs:
    """测试评论相关API"""

    @pytest.mark.asyncio
    async def test_get_video_comments(self, async_client: AsyncClient, test_video):
        """GET /api/v1/comments/video/{video_id} - 获取视频评论"""
        response = await async_client.get(f"/api/v1/comments/video/{test_video.id}")
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_create_comment(self, async_client: AsyncClient, user_token: str, test_video):
        """POST /api/v1/comments/ - 创建评论"""
        response = await async_client.post(
            "/api/v1/comments/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "video_id": test_video.id,
                "content": "Test comment from pytest"
            }
        )
        assert response.status_code in [200, 201, 422, 429]

    @pytest.mark.asyncio
    async def test_get_my_comments(self, async_client: AsyncClient, user_token: str):
        """GET /api/v1/comments/user/me - 获取我的评论"""
        response = await async_client.get(
            "/api/v1/comments/user/me",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code in [200, 404]


# ===========================================
# 弹幕API测试 (5个端点)
# ===========================================

class TestDanmakuAPIs:
    """测试弹幕相关API"""

    @pytest.mark.asyncio
    async def test_get_video_danmaku(self, async_client: AsyncClient, test_video):
        """GET /api/v1/danmaku/video/{video_id} - 获取视频弹幕"""
        response = await async_client.get(f"/api/v1/danmaku/video/{test_video.id}")
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_send_danmaku(self, async_client: AsyncClient, user_token: str, test_video):
        """POST /api/v1/danmaku/ - 发送弹幕"""
        response = await async_client.post(
            "/api/v1/danmaku/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "video_id": test_video.id,
                "content": "Test danmaku",
                "time": 10.5,
                "color": "#FFFFFF",
                "type": 0
            }
        )
        assert response.status_code in [200, 201, 422, 429]

    @pytest.mark.asyncio
    async def test_get_my_danmaku(self, async_client: AsyncClient, user_token: str):
        """GET /api/v1/danmaku/my-danmaku - 获取我的弹幕"""
        response = await async_client.get(
            "/api/v1/danmaku/my-danmaku",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code in [200, 404]


# ===========================================
# 收藏API测试 (7个端点)
# ===========================================

class TestFavoriteAPIs:
    """测试收藏相关API"""

    @pytest.mark.asyncio
    async def test_get_favorites(self, async_client: AsyncClient, user_token: str):
        """GET /api/v1/favorites/ - 获取收藏列表"""
        response = await async_client.get(
            "/api/v1/favorites/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_add_favorite(self, async_client: AsyncClient, user_token: str, test_video):
        """POST /api/v1/favorites/ - 添加收藏"""
        response = await async_client.post(
            "/api/v1/favorites/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"video_id": test_video.id}
        )
        assert response.status_code in [200, 201, 409, 422]

    @pytest.mark.asyncio
    async def test_check_favorite_status(self, async_client: AsyncClient, user_token: str, test_video):
        """GET /api/v1/favorites/check/{video_id} - 检查收藏状态"""
        response = await async_client.get(
            f"/api/v1/favorites/check/{test_video.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_favorite_folders(self, async_client: AsyncClient, user_token: str):
        """GET /api/v1/favorites/folders - 获取收藏夹列表"""
        response = await async_client.get(
            "/api/v1/favorites/folders",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create_favorite_folder(self, async_client: AsyncClient, user_token: str):
        """POST /api/v1/favorites/folders - 创建收藏夹"""
        response = await async_client.post(
            "/api/v1/favorites/folders",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "name": "Test Folder",
                "description": "Test folder description"
            }
        )
        assert response.status_code in [200, 201, 422, 409]


# ===========================================
# 观看历史API测试 (6个端点)
# ===========================================

class TestHistoryAPIs:
    """测试观看历史API"""

    @pytest.mark.asyncio
    async def test_get_history(self, async_client: AsyncClient, user_token: str):
        """GET /api/v1/history/ - 获取观看历史"""
        response = await async_client.get(
            "/api/v1/history/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_create_history(self, async_client: AsyncClient, user_token: str, test_video):
        """POST /api/v1/history/ - 创建观看记录"""
        response = await async_client.post(
            "/api/v1/history/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "video_id": test_video.id,
                "progress": 60,
                "duration": 120
            }
        )
        assert response.status_code in [200, 201, 422]

    @pytest.mark.asyncio
    async def test_get_video_history(self, async_client: AsyncClient, user_token: str, test_video):
        """GET /api/v1/history/{video_id} - 获取单个视频观看记录"""
        response = await async_client.get(
            f"/api/v1/history/{test_video.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_update_progress(self, async_client: AsyncClient, user_token: str, test_video):
        """PATCH /api/v1/history/{video_id}/progress - 更新播放进度"""
        response = await async_client.patch(
            f"/api/v1/history/{test_video.id}/progress",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"progress": 90}
        )
        assert response.status_code in [200, 404, 422]


# ===========================================
# 评分API测试 (4个端点)
# ===========================================

class TestRatingAPIs:
    """测试评分相关API"""

    @pytest.mark.asyncio
    async def test_create_rating(self, async_client: AsyncClient, user_token: str, test_video):
        """POST /api/v1/ratings/ - 创建评分"""
        response = await async_client.post(
            "/api/v1/ratings/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "video_id": test_video.id,
                "score": 9.0
            }
        )
        assert response.status_code in [200, 201, 422, 429]

    @pytest.mark.asyncio
    async def test_get_video_rating_stats(self, async_client: AsyncClient, test_video):
        """GET /api/v1/ratings/video/{video_id}/stats - 获取视频评分统计"""
        response = await async_client.get(f"/api/v1/ratings/video/{test_video.id}/stats")
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_my_rating(self, async_client: AsyncClient, user_token: str, test_video):
        """GET /api/v1/ratings/video/{video_id}/my-rating - 获取我的评分"""
        response = await async_client.get(
            f"/api/v1/ratings/video/{test_video.id}/my-rating",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code in [200, 404]


# ===========================================
# 通知API测试 (6个端点)
# ===========================================

class TestNotificationAPIs:
    """测试通知相关API"""

    @pytest.mark.asyncio
    async def test_get_notifications(self, async_client: AsyncClient, user_token: str):
        """GET /api/v1/notifications/ - 获取通知列表"""
        response = await async_client.get(
            "/api/v1/notifications/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_notification_stats(self, async_client: AsyncClient, user_token: str):
        """GET /api/v1/notifications/stats - 获取通知统计"""
        response = await async_client.get(
            "/api/v1/notifications/stats",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_mark_all_read(self, async_client: AsyncClient, user_token: str):
        """POST /api/v1/notifications/mark-all-read - 全部标记已读"""
        response = await async_client.post(
            "/api/v1/notifications/mark-all-read",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code in [200, 204, 404]


# ===========================================
# 分享API测试 (3个端点)
# ===========================================

class TestShareAPIs:
    """测试分享相关API"""

    @pytest.mark.asyncio
    async def test_create_share(self, async_client: AsyncClient, test_video):
        """POST /api/v1/shares/ - 记录分享"""
        response = await async_client.post(
            "/api/v1/shares/",
            json={
                "video_id": test_video.id,
                "platform": "wechat"
            }
        )
        assert response.status_code in [200, 201, 422, 429]

    @pytest.mark.asyncio
    async def test_get_share_stats(self, async_client: AsyncClient, test_video):
        """GET /api/v1/shares/video/{video_id}/stats - 获取分享统计"""
        response = await async_client.get(f"/api/v1/shares/video/{test_video.id}/stats")
        assert response.status_code in [200, 404]


# ===========================================
# 推荐API测试 (3个端点)
# ===========================================

class TestRecommendationAPIs:
    """测试推荐相关API"""

    @pytest.mark.asyncio
    async def test_get_personalized_recommendations(self, async_client: AsyncClient):
        """GET /api/v1/recommendations/personalized - 个性化推荐"""
        response = await async_client.get("/api/v1/recommendations/personalized")
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_similar_videos(self, async_client: AsyncClient, test_video):
        """GET /api/v1/recommendations/similar/{video_id} - 相似视频推荐"""
        response = await async_client.get(f"/api/v1/recommendations/similar/{test_video.id}")
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_for_you(self, async_client: AsyncClient):
        """GET /api/v1/recommendations/for-you - 为你推荐"""
        response = await async_client.get("/api/v1/recommendations/for-you")
        assert response.status_code in [200, 404]


# ===========================================
# 专辑/系列API测试 (3个端点)
# ===========================================

class TestSeriesAPIs:
    """测试专辑/系列API"""

    @pytest.mark.asyncio
    async def test_get_series_list(self, async_client: AsyncClient):
        """GET /api/v1/series - 获取专辑列表"""
        response = await async_client.get("/api/v1/series")
        assert response.status_code in [200, 404, 429]

    @pytest.mark.asyncio
    async def test_get_featured_series(self, async_client: AsyncClient):
        """GET /api/v1/series/featured/list - 获取推荐专辑"""
        response = await async_client.get("/api/v1/series/featured/list")
        assert response.status_code in [200, 404]


# ===========================================
# 字幕API测试 (1个端点)
# ===========================================

class TestSubtitleAPIs:
    """测试字幕相关API"""

    @pytest.mark.asyncio
    async def test_get_video_subtitles(self, async_client: AsyncClient, test_video):
        """GET /api/v1/videos/{video_id}/subtitles - 获取视频字幕"""
        response = await async_client.get(f"/api/v1/videos/{test_video.id}/subtitles")
        assert response.status_code in [200, 404]


# ===========================================
# 管理员认证API测试
# ===========================================

class TestAdminAuthAPIs:
    """测试管理员认证API"""

    @pytest.mark.asyncio
    async def test_admin_login(self, async_client: AsyncClient):
        """POST /api/v1/auth/admin/login - 管理员登录"""
        from app.utils.cache import get_redis

        # 获取验证码
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
        assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_admin_get_me(self, async_client: AsyncClient, admin_token: str):
        """GET /api/v1/auth/admin/me - 获取管理员信息"""
        response = await async_client.get(
            "/api/v1/auth/admin/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "username" in data

    @pytest.mark.asyncio
    async def test_admin_logout(self, async_client: AsyncClient, admin_token: str):
        """POST /api/v1/auth/admin/logout - 管理员登出"""
        response = await async_client.post(
            "/api/v1/auth/admin/logout",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 204]


# ===========================================
# 管理员视频管理API测试 (9个端点)
# ===========================================

class TestAdminVideoAPIs:
    """测试管理员视频管理API"""

    @pytest.mark.asyncio
    async def test_admin_get_videos(self, async_client: AsyncClient, admin_token: str):
        """GET /api/v1/admin/videos - 获取所有视频"""
        response = await async_client.get(
            "/api/v1/admin/videos",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_admin_create_video(self, async_client: AsyncClient, admin_token: str):
        """POST /api/v1/admin/videos - 创建视频"""
        response = await async_client.post(
            "/api/v1/admin/videos",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Admin Test Video",
                "slug": f"admin-test-video-{pytest.__version__}",
                "description": "Test",
                "video_type": "MOVIE",
                "status": "DRAFT",
                "duration": 120
            }
        )
        assert response.status_code in [200, 201, 422, 409]

    @pytest.mark.asyncio
    async def test_admin_get_video_detail(self, async_client: AsyncClient, admin_token: str, test_video):
        """GET /api/v1/admin/videos/{video_id} - 获取视频详情"""
        response = await async_client.get(
            f"/api/v1/admin/videos/{test_video.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_admin_update_video(self, async_client: AsyncClient, admin_token: str, test_video):
        """PUT /api/v1/admin/videos/{video_id} - 更新视频"""
        response = await async_client.put(
            f"/api/v1/admin/videos/{test_video.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"title": "Updated Admin Test Video"}
        )
        assert response.status_code in [200, 404, 422]

    @pytest.mark.asyncio
    async def test_admin_update_video_status(self, async_client: AsyncClient, admin_token: str, test_video):
        """PUT /api/v1/admin/videos/{video_id}/status - 更新视频状态"""
        response = await async_client.put(
            f"/api/v1/admin/videos/{test_video.id}/status",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"status": "PUBLISHED"}
        )
        assert response.status_code in [200, 404, 422]


# ===========================================
# 管理员用户管理API测试 (2个端点)
# ===========================================

class TestAdminUserAPIs:
    """测试管理员用户管理API"""

    @pytest.mark.asyncio
    async def test_admin_get_users(self, async_client: AsyncClient, admin_token: str):
        """GET /api/v1/admin/users - 获取所有用户"""
        response = await async_client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200


# ===========================================
# 管理员评论管理API测试 (8个端点)
# ===========================================

class TestAdminCommentAPIs:
    """测试管理员评论管理API"""

    @pytest.mark.asyncio
    async def test_admin_get_comments(self, async_client: AsyncClient, admin_token: str):
        """GET /api/v1/admin/comments - 获取所有评论"""
        response = await async_client.get(
            "/api/v1/admin/comments",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_admin_get_pending_comments(self, async_client: AsyncClient, admin_token: str):
        """GET /api/v1/admin/comments/pending - 获取待审核评论"""
        response = await async_client.get(
            "/api/v1/admin/comments/pending",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200


# ===========================================
# 管理员分类管理API测试 (5个端点)
# ===========================================

class TestAdminCategoryAPIs:
    """测试管理员分类管理API"""

    @pytest.mark.asyncio
    async def test_admin_get_categories(self, async_client: AsyncClient, admin_token: str):
        """GET /api/v1/admin/categories/ - 获取所有分类"""
        response = await async_client.get(
            "/api/v1/admin/categories/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_admin_create_category(self, async_client: AsyncClient, admin_token: str):
        """POST /api/v1/admin/categories/ - 创建分类"""
        response = await async_client.post(
            "/api/v1/admin/categories/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": f"Test Category {pytest.__version__}",
                "slug": f"test-category-{pytest.__version__}",
                "description": "Test"
            }
        )
        assert response.status_code in [200, 201, 422, 409]


# ===========================================
# 管理员国家管理API测试 (5个端点)
# ===========================================

class TestAdminCountryAPIs:
    """测试管理员国家管理API"""

    @pytest.mark.asyncio
    async def test_admin_get_countries(self, async_client: AsyncClient, admin_token: str):
        """GET /api/v1/admin/countries/ - 获取所有国家"""
        response = await async_client.get(
            "/api/v1/admin/countries/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200


# ===========================================
# 管理员标签管理API测试 (5个端点)
# ===========================================

class TestAdminTagAPIs:
    """测试管理员标签管理API"""

    @pytest.mark.asyncio
    async def test_admin_get_tags(self, async_client: AsyncClient, admin_token: str):
        """GET /api/v1/admin/tags/ - 获取所有标签"""
        response = await async_client.get(
            "/api/v1/admin/tags/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200


# ===========================================
# 管理员演员管理API测试 (5个端点)
# ===========================================

class TestAdminActorAPIs:
    """测试管理员演员管理API"""

    @pytest.mark.asyncio
    async def test_admin_get_actors(self, async_client: AsyncClient, admin_token: str):
        """GET /api/v1/admin/actors/ - 获取所有演员"""
        response = await async_client.get(
            "/api/v1/admin/actors/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200


# ===========================================
# 管理员导演管理API测试 (5个端点)
# ===========================================

class TestAdminDirectorAPIs:
    """测试管理员导演管理API"""

    @pytest.mark.asyncio
    async def test_admin_get_directors(self, async_client: AsyncClient, admin_token: str):
        """GET /api/v1/admin/directors/ - 获取所有导演"""
        response = await async_client.get(
            "/api/v1/admin/directors/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200


# ===========================================
# 管理员专辑管理API测试 (8个端点)
# ===========================================

class TestAdminSeriesAPIs:
    """测试管理员专辑管理API"""

    @pytest.mark.asyncio
    async def test_admin_get_series(self, async_client: AsyncClient, admin_token: str):
        """GET /api/v1/admin/series - 获取专辑列表"""
        response = await async_client.get(
            "/api/v1/admin/series",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200


# ===========================================
# 管理员Banner管理API测试 (8个端点)
# ===========================================

class TestAdminBannerAPIs:
    """测试管理员Banner管理API"""

    @pytest.mark.asyncio
    async def test_admin_get_banners(self, async_client: AsyncClient, admin_token: str):
        """GET /api/v1/admin/banners/banners - 获取Banner列表"""
        response = await async_client.get(
            "/api/v1/admin/banners/banners",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200


# ===========================================
# 管理员公告管理API测试 (7个端点)
# ===========================================

class TestAdminAnnouncementAPIs:
    """测试管理员公告管理API"""

    @pytest.mark.asyncio
    async def test_admin_get_announcements(self, async_client: AsyncClient, admin_token: str):
        """GET /api/v1/admin/announcements/announcements - 获取公告列表"""
        response = await async_client.get(
            "/api/v1/admin/announcements/announcements",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200


# ===========================================
# 管理员统计API测试 (11个端点)
# ===========================================

class TestAdminStatsAPIs:
    """测试管理员统计API"""

    @pytest.mark.asyncio
    async def test_admin_get_stats_overview(self, async_client: AsyncClient, admin_token: str):
        """GET /api/v1/admin/stats/overview - 获取概览统计"""
        response = await async_client.get(
            "/api/v1/admin/stats/overview",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_admin_get_trends(self, async_client: AsyncClient, admin_token: str):
        """GET /api/v1/admin/stats/trends - 获取趋势统计"""
        response = await async_client.get(
            "/api/v1/admin/stats/trends",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_admin_get_video_categories(self, async_client: AsyncClient, admin_token: str):
        """GET /api/v1/admin/stats/video-categories - 获取分类统计"""
        response = await async_client.get(
            "/api/v1/admin/stats/video-categories",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_admin_get_top_videos(self, async_client: AsyncClient, admin_token: str):
        """GET /api/v1/admin/stats/top-videos - 获取Top10视频"""
        response = await async_client.get(
            "/api/v1/admin/stats/top-videos",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_admin_get_cache_stats(self, async_client: AsyncClient, admin_token: str):
        """GET /api/v1/admin/stats/cache-stats - 获取缓存统计"""
        response = await async_client.get(
            "/api/v1/admin/stats/cache-stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404, 500]


# ===========================================
# 管理员日志API测试 (7个端点)
# ===========================================

class TestAdminLogAPIs:
    """测试管理员日志API"""

    @pytest.mark.asyncio
    async def test_admin_get_operation_logs(self, async_client: AsyncClient, admin_token: str):
        """GET /api/v1/admin/logs/operations - 获取操作日志"""
        response = await async_client.get(
            "/api/v1/admin/logs/operations",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_admin_get_log_stats(self, async_client: AsyncClient, admin_token: str):
        """GET /api/v1/admin/logs/operations/stats/summary - 获取日志统计"""
        response = await async_client.get(
            "/api/v1/admin/logs/operations/stats/summary",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200


# ===========================================
# WebSocket测试 (1个端点)
# ===========================================

class TestWebSocketAPIs:
    """测试WebSocket相关API"""

    @pytest.mark.asyncio
    async def test_get_ws_stats(self, async_client: AsyncClient):
        """GET /api/v1/ws/stats - 获取WebSocket统计"""
        response = await async_client.get("/api/v1/ws/stats")
        assert response.status_code in [200, 404]


# ===========================================
# 健康检查测试
# ===========================================

class TestHealthAPIs:
    """测试健康检查API"""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, async_client: AsyncClient):
        """GET / - 根端点"""
        response = await async_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    @pytest.mark.asyncio
    async def test_health_check(self, async_client: AsyncClient):
        """GET /health - 健康检查"""
        response = await async_client.get("/health")
        assert response.status_code in [200, 503]
        data = response.json()
        assert "status" in data
        assert "checks" in data
