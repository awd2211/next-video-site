"""
测试 Admin 核心管理 API
包括: videos, users, comments, stats, logs, dashboard_config, reports, video_analytics
"""
import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminVideosAPI:
    """管理员视频管理 API 测试"""

    async def test_get_videos_list(self, async_client: AsyncClient, admin_token: str):
        """测试获取视频列表"""
        response = await async_client.get(
            "/api/v1/admin/videos",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    async def test_get_videos_with_filters(self, async_client: AsyncClient, admin_token: str):
        """测试带筛选条件的视频列表"""
        response = await async_client.get(
            "/api/v1/admin/videos?status=published&page=1&page_size=10",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    async def test_get_video_detail(self, async_client: AsyncClient, admin_token: str):
        """测试获取视频详情"""
        response = await async_client.get(
            "/api/v1/admin/videos/1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_create_video_success(self, async_client: AsyncClient, admin_token: str):
        """测试创建视频 - 成功"""
        video_data = {
            "title": "Test Admin Video",
            "slug": "test-admin-video-pytest",
            "video_type": "movie",
            "status": "draft",
            "description": "Test description"
        }
        response = await async_client.post(
            "/api/v1/admin/videos",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=video_data
        )
        assert response.status_code in [200, 201, 422]  # 422 if slug exists

    async def test_update_video(self, async_client: AsyncClient, admin_token: str):
        """测试更新视频"""
        update_data = {"title": "Updated Title", "status": "published"}
        response = await async_client.put(
            "/api/v1/admin/videos/1",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=update_data
        )
        assert response.status_code in [200, 404, 422]

    async def test_delete_video(self, async_client: AsyncClient, admin_token: str):
        """测试删除视频"""
        response = await async_client.delete(
            "/api/v1/admin/videos/999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 204, 404]

    async def test_videos_unauthorized(self, async_client: AsyncClient):
        """测试未授权访问"""
        response = await async_client.get("/api/v1/admin/videos")
        assert response.status_code in [401, 403]

    async def test_videos_regular_user_forbidden(self, async_client: AsyncClient, user_token: str):
        """测试普通用户访问管理员 API"""
        response = await async_client.get(
            "/api/v1/admin/videos",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminUsersAPI:
    """管理员用户管理 API 测试"""

    async def test_get_users_list(self, async_client: AsyncClient, admin_token: str):
        """测试获取用户列表"""
        response = await async_client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or "users" in data or isinstance(data, list)

    async def test_get_user_detail(self, async_client: AsyncClient, admin_token: str):
        """测试获取用户详情"""
        response = await async_client.get(
            "/api/v1/admin/users/1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_ban_user(self, async_client: AsyncClient, admin_token: str):
        """测试封禁用户"""
        response = await async_client.post(
            "/api/v1/admin/users/999/ban",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"reason": "Test ban"}
        )
        assert response.status_code in [200, 404, 422]

    async def test_unban_user(self, async_client: AsyncClient, admin_token: str):
        """测试解封用户"""
        response = await async_client.post(
            "/api/v1/admin/users/999/unban",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404, 422]

    async def test_users_unauthorized(self, async_client: AsyncClient):
        """测试未授权访问用户管理"""
        response = await async_client.get("/api/v1/admin/users")
        assert response.status_code in [401, 403]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminCommentsAPI:
    """管理员评论管理 API 测试"""

    async def test_get_comments_list(self, async_client: AsyncClient, admin_token: str):
        """测试获取评论列表"""
        response = await async_client.get(
            "/api/v1/admin/comments",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    async def test_approve_comment(self, async_client: AsyncClient, admin_token: str):
        """测试审核通过评论"""
        response = await async_client.post(
            "/api/v1/admin/comments/1/approve",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_reject_comment(self, async_client: AsyncClient, admin_token: str):
        """测试拒绝评论"""
        response = await async_client.post(
            "/api/v1/admin/comments/1/reject",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_delete_comment(self, async_client: AsyncClient, admin_token: str):
        """测试删除评论"""
        response = await async_client.delete(
            "/api/v1/admin/comments/999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 204, 404]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminStatsAPI:
    """管理员统计数据 API 测试"""

    async def test_get_overview_stats(self, async_client: AsyncClient, admin_token: str):
        """测试获取概览统计"""
        response = await async_client.get(
            "/api/v1/admin/stats/overview",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        # 应该包含用户数、视频数等统计
        assert isinstance(data, dict)

    async def test_get_video_stats(self, async_client: AsyncClient, admin_token: str):
        """测试获取视频统计"""
        response = await async_client.get(
            "/api/v1/admin/stats/videos",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_get_user_stats(self, async_client: AsyncClient, admin_token: str):
        """测试获取用户统计"""
        response = await async_client.get(
            "/api/v1/admin/stats/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_stats_unauthorized(self, async_client: AsyncClient):
        """测试未授权访问统计"""
        response = await async_client.get("/api/v1/admin/stats/overview")
        assert response.status_code in [401, 403]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminLogsAPI:
    """管理员日志管理 API 测试"""

    async def test_get_operation_logs(self, async_client: AsyncClient, admin_token: str):
        """测试获取操作日志"""
        response = await async_client.get(
            "/api/v1/admin/logs/operations",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_get_error_logs(self, async_client: AsyncClient, admin_token: str):
        """测试获取错误日志"""
        response = await async_client.get(
            "/api/v1/admin/logs/errors",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_get_login_logs(self, async_client: AsyncClient, admin_token: str):
        """测试获取登录日志"""
        response = await async_client.get(
            "/api/v1/admin/logs/logins",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_logs_with_filters(self, async_client: AsyncClient, admin_token: str):
        """测试带筛选的日志查询"""
        response = await async_client.get(
            "/api/v1/admin/logs/operations?page=1&page_size=20",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminDashboardAPI:
    """管理员仪表盘配置 API 测试"""

    async def test_get_dashboard_config(self, async_client: AsyncClient, admin_token: str):
        """测试获取仪表盘配置"""
        response = await async_client.get(
            "/api/v1/admin/dashboard/config",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_save_dashboard_config(self, async_client: AsyncClient, admin_token: str):
        """测试保存仪表盘配置"""
        config_data = {
            "layout": [{"i": "1", "x": 0, "y": 0, "w": 2, "h": 2}]
        }
        response = await async_client.post(
            "/api/v1/admin/dashboard/config",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=config_data
        )
        assert response.status_code in [200, 201, 422]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminReportsAPI:
    """管理员报表 API 测试"""

    async def test_generate_video_report(self, async_client: AsyncClient, admin_token: str):
        """测试生成视频报表"""
        response = await async_client.get(
            "/api/v1/admin/reports/videos",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_generate_user_report(self, async_client: AsyncClient, admin_token: str):
        """测试生成用户报表"""
        response = await async_client.get(
            "/api/v1/admin/reports/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_export_report(self, async_client: AsyncClient, admin_token: str):
        """测试导出报表"""
        response = await async_client.get(
            "/api/v1/admin/reports/export?type=videos",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404, 422]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminVideoAnalyticsAPI:
    """管理员视频分析 API 测试"""

    async def test_get_video_analytics(self, async_client: AsyncClient, admin_token: str):
        """测试获取视频分析数据"""
        response = await async_client.get(
            "/api/v1/admin/videos/1/analytics",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_get_trending_videos(self, async_client: AsyncClient, admin_token: str):
        """测试获取热门视频分析"""
        response = await async_client.get(
            "/api/v1/admin/analytics/trending",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

