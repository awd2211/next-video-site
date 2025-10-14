"""
测试 app/middleware/ - 请求相关中间件
"""
import pytest
import uuid
from httpx import AsyncClient


@pytest.mark.middleware
@pytest.mark.asyncio
class TestRequestIDMiddleware:
    """请求 ID 中间件测试"""

    async def test_adds_request_id_to_response(self, async_client: AsyncClient):
        """测试添加请求 ID 到响应头"""
        response = await async_client.get("/")
        
        assert "x-request-id" in response.headers
        request_id = response.headers["x-request-id"]
        assert len(request_id) > 0

    async def test_generates_unique_ids(self, async_client: AsyncClient):
        """测试生成唯一的请求 ID"""
        response1 = await async_client.get("/")
        response2 = await async_client.get("/")
        
        id1 = response1.headers.get("x-request-id")
        id2 = response2.headers.get("x-request-id")
        
        assert id1 != id2

    async def test_accepts_client_request_id(self, async_client: AsyncClient):
        """测试接受客户端提供的请求 ID"""
        client_id = str(uuid.uuid4())
        response = await async_client.get(
            "/",
            headers={"X-Request-ID": client_id}
        )
        
        assert response.headers["x-request-id"] == client_id

    async def test_request_id_is_valid_uuid(self, async_client: AsyncClient):
        """测试生成的请求 ID 是有效的 UUID"""
        response = await async_client.get("/")
        request_id = response.headers["x-request-id"]
        
        # 验证是有效的 UUID
        try:
            uuid.UUID(request_id)
            assert True
        except ValueError:
            assert False, f"Invalid UUID: {request_id}"


@pytest.mark.middleware
@pytest.mark.asyncio
class TestRequestSizeLimitMiddleware:
    """请求大小限制中间件测试"""

    async def test_accepts_normal_request(self, async_client: AsyncClient):
        """测试接受正常大小的请求"""
        data = {"test": "data"}
        response = await async_client.post("/api/v1/auth/login", json=data)
        
        # 应该被接受（即使可能失败，但不是因为大小）
        assert response.status_code != 413

    async def test_small_request_body(self, async_client: AsyncClient):
        """测试小请求体"""
        data = {"key": "value"}
        response = await async_client.post("/test", json=data)
        
        assert response.status_code != 413

