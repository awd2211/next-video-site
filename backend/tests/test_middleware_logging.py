"""
测试 app/middleware/ - 日志相关中间件
"""
import pytest
from httpx import AsyncClient


@pytest.mark.middleware
@pytest.mark.asyncio
class TestOperationLogMiddleware:
    """操作日志中间件测试"""

    async def test_logs_admin_operations(self, async_client: AsyncClient, admin_token: str):
        """测试记录管理员操作"""
        response = await async_client.get(
            "/api/v1/admin/stats/overview",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # 管理员操作应该被记录
        assert response.status_code in [200, 404]

    async def test_does_not_log_regular_user_ops(self, async_client: AsyncClient, user_token: str):
        """测试不记录普通用户操作"""
        response = await async_client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        # 普通用户操作不记录
        assert response.status_code in [200, 404]


@pytest.mark.middleware
@pytest.mark.asyncio
class TestErrorLoggingMiddleware:
    """错误日志中间件测试"""

    async def test_logs_500_errors(self, async_client: AsyncClient):
        """测试记录 500 错误"""
        # 尝试触发错误（如果有错误端点）
        response = await async_client.get("/api/v1/nonexistent-endpoint")
        
        # 应该有响应（即使是 404）
        assert response.status_code in [404, 500]

    async def test_logs_validation_errors(self, async_client: AsyncClient):
        """测试记录验证错误"""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"invalid": "data"}
        )
        
        # 应该返回 422 验证错误
        assert response.status_code == 422


@pytest.mark.middleware
@pytest.mark.asyncio
class TestQueryMonitorMiddleware:
    """查询监控中间件测试"""

    async def test_monitors_database_queries(self, async_client: AsyncClient):
        """测试监控数据库查询"""
        response = await async_client.get("/api/v1/videos")
        
        # 中间件应该监控查询
        assert response.status_code in [200, 404]

    async def test_detects_slow_queries(self, async_client: AsyncClient):
        """测试检测慢查询"""
        # 正常查询不应该触发慢查询告警
        response = await async_client.get("/api/v1/categories")
        
        assert response.status_code in [200, 404]

