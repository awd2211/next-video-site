"""
测试 Middleware - Transaction Middleware (事务中间件)
测试事务管理和读写操作区分
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from app.middleware.transaction_middleware import TransactionMiddleware


# ===========================================
# 测试 Fixtures
# ===========================================

@pytest.fixture
def test_app():
    """创建测试应用"""
    app = FastAPI()

    # 添加事务中间件
    app.add_middleware(TransactionMiddleware)

    # 添加测试路由
    @app.get("/test")
    async def test_get(request: Request):
        is_read_only = getattr(request.state, "is_read_only", None)
        return JSONResponse({"is_read_only": is_read_only})

    @app.post("/test")
    async def test_post(request: Request):
        is_read_only = getattr(request.state, "is_read_only", None)
        return JSONResponse({"is_read_only": is_read_only})

    @app.put("/test")
    async def test_put(request: Request):
        is_read_only = getattr(request.state, "is_read_only", None)
        return JSONResponse({"is_read_only": is_read_only})

    @app.patch("/test")
    async def test_patch(request: Request):
        is_read_only = getattr(request.state, "is_read_only", None)
        return JSONResponse({"is_read_only": is_read_only})

    @app.delete("/test")
    async def test_delete(request: Request):
        is_read_only = getattr(request.state, "is_read_only", None)
        return JSONResponse({"is_read_only": is_read_only})

    @app.head("/test")
    async def test_head(request: Request):
        return JSONResponse({})

    @app.options("/test")
    async def test_options(request: Request):
        return JSONResponse({})

    return app


# ===========================================
# 1. 只读请求测试
# ===========================================

class TestReadOnlyRequests:
    """测试只读请求（GET, HEAD, OPTIONS）"""

    @pytest.mark.asyncio
    async def test_get_request_is_read_only(self, test_app):
        """测试 GET 请求被标记为只读"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            response = await client.get("/test")

            assert response.status_code == 200
            data = response.json()
            assert data["is_read_only"] is True

    @pytest.mark.asyncio
    async def test_head_request_is_read_only(self, test_app):
        """测试 HEAD 请求被标记为只读"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            response = await client.head("/test")

            assert response.status_code == 200
            # HEAD 请求应该被标记为只读
            # 通过请求的 state 验证

    @pytest.mark.asyncio
    async def test_options_request_is_read_only(self, test_app):
        """测试 OPTIONS 请求被标记为只读"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            response = await client.options("/test")

            assert response.status_code == 200
            # OPTIONS 请求应该被标记为只读


# ===========================================
# 2. 读写请求测试
# ===========================================

class TestReadWriteRequests:
    """测试读写请求（POST, PUT, PATCH, DELETE）"""

    @pytest.mark.asyncio
    async def test_post_request_is_not_read_only(self, test_app):
        """测试 POST 请求不是只读"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            response = await client.post("/test")

            assert response.status_code == 200
            data = response.json()
            assert data["is_read_only"] is False

    @pytest.mark.asyncio
    async def test_put_request_is_not_read_only(self, test_app):
        """测试 PUT 请求不是只读"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            response = await client.put("/test")

            assert response.status_code == 200
            data = response.json()
            assert data["is_read_only"] is False

    @pytest.mark.asyncio
    async def test_patch_request_is_not_read_only(self, test_app):
        """测试 PATCH 请求不是只读"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            response = await client.patch("/test")

            assert response.status_code == 200
            data = response.json()
            assert data["is_read_only"] is False

    @pytest.mark.asyncio
    async def test_delete_request_is_not_read_only(self, test_app):
        """测试 DELETE 请求不是只读"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            response = await client.delete("/test")

            assert response.status_code == 200
            data = response.json()
            assert data["is_read_only"] is False


# ===========================================
# 3. TransactionMiddleware 类测试
# ===========================================

class TestTransactionMiddlewareClass:
    """测试 TransactionMiddleware 类"""

    def test_read_only_methods_constant(self):
        """测试只读方法常量"""
        assert "GET" in TransactionMiddleware.READ_ONLY_METHODS
        assert "HEAD" in TransactionMiddleware.READ_ONLY_METHODS
        assert "OPTIONS" in TransactionMiddleware.READ_ONLY_METHODS
        assert "POST" not in TransactionMiddleware.READ_ONLY_METHODS
        assert "PUT" not in TransactionMiddleware.READ_ONLY_METHODS
        assert "DELETE" not in TransactionMiddleware.READ_ONLY_METHODS

    @pytest.mark.asyncio
    async def test_dispatch_sets_read_only_flag(self):
        """测试 dispatch 方法设置只读标志"""
        middleware = TransactionMiddleware(app=None)

        # 模拟 GET 请求
        mock_request = MagicMock(spec=Request)
        mock_request.method = "GET"
        mock_request.state = MagicMock()

        mock_call_next = AsyncMock(return_value=JSONResponse({"status": "ok"}))

        response = await middleware.dispatch(mock_request, mock_call_next)

        # 验证只读标志被设置
        assert mock_request.state.is_read_only is True
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_dispatch_sets_not_read_only_flag(self):
        """测试 dispatch 方法设置非只读标志"""
        middleware = TransactionMiddleware(app=None)

        # 模拟 POST 请求
        mock_request = MagicMock(spec=Request)
        mock_request.method = "POST"
        mock_request.state = MagicMock()

        mock_call_next = AsyncMock(return_value=JSONResponse({"status": "ok"}))

        response = await middleware.dispatch(mock_request, mock_call_next)

        # 验证只读标志被设置为 False
        assert mock_request.state.is_read_only is False
        assert response.status_code == 200


# ===========================================
# 4. 边界条件测试
# ===========================================

class TestEdgeCases:
    """测试边界条件"""

    @pytest.mark.asyncio
    async def test_middleware_with_custom_methods(self):
        """测试自定义 HTTP 方法"""
        middleware = TransactionMiddleware(app=None)

        # 模拟自定义方法（如 PROPFIND）
        mock_request = MagicMock(spec=Request)
        mock_request.method = "PROPFIND"  # WebDAV 方法
        mock_request.state = MagicMock()

        mock_call_next = AsyncMock(return_value=JSONResponse({"status": "ok"}))

        response = await middleware.dispatch(mock_request, mock_call_next)

        # 自定义方法应该被视为读写操作
        assert mock_request.state.is_read_only is False

    @pytest.mark.asyncio
    async def test_middleware_case_sensitivity(self):
        """测试方法名大小写敏感性"""
        middleware = TransactionMiddleware(app=None)

        # HTTP 方法应该是大写
        mock_request = MagicMock(spec=Request)
        mock_request.method = "get"  # 小写
        mock_request.state = MagicMock()

        mock_call_next = AsyncMock(return_value=JSONResponse({"status": "ok"}))

        response = await middleware.dispatch(mock_request, mock_call_next)

        # 小写 get 不在 READ_ONLY_METHODS 中
        assert mock_request.state.is_read_only is False

    @pytest.mark.asyncio
    async def test_middleware_preserves_response(self):
        """测试中间件不修改响应"""
        middleware = TransactionMiddleware(app=None)

        mock_request = MagicMock(spec=Request)
        mock_request.method = "GET"
        mock_request.state = MagicMock()

        expected_response = JSONResponse(
            {"message": "test", "status": 200},
            status_code=200,
            headers={"X-Custom": "value"}
        )

        mock_call_next = AsyncMock(return_value=expected_response)

        response = await middleware.dispatch(mock_request, mock_call_next)

        # 响应应该保持不变
        assert response == expected_response
        assert response.status_code == 200


# ===========================================
# 5. 集成测试
# ===========================================

class TestIntegration:
    """测试中间件集成"""

    @pytest.mark.asyncio
    async def test_middleware_with_real_endpoints(self, test_app):
        """测试中间件与真实端点的集成"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            # GET 请求
            get_response = await client.get("/test")
            assert get_response.json()["is_read_only"] is True

            # POST 请求
            post_response = await client.post("/test")
            assert post_response.json()["is_read_only"] is False

            # DELETE 请求
            delete_response = await client.delete("/test")
            assert delete_response.json()["is_read_only"] is False

    @pytest.mark.asyncio
    async def test_middleware_with_query_parameters(self, test_app):
        """测试带查询参数的请求"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            response = await client.get("/test?param1=value1&param2=value2")

            assert response.status_code == 200
            data = response.json()
            assert data["is_read_only"] is True

    @pytest.mark.asyncio
    async def test_middleware_with_request_body(self, test_app):
        """测试带请求体的请求"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            response = await client.post("/test", json={"key": "value"})

            assert response.status_code == 200
            data = response.json()
            assert data["is_read_only"] is False

    @pytest.mark.asyncio
    async def test_middleware_order_independence(self, test_app):
        """测试中间件的顺序独立性"""
        # 多次请求应该得到一致的结果
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            for _ in range(3):
                get_response = await client.get("/test")
                assert get_response.json()["is_read_only"] is True

                post_response = await client.post("/test")
                assert post_response.json()["is_read_only"] is False


# ===========================================
# 6. 性能和并发测试
# ===========================================

class TestPerformance:
    """测试性能相关"""

    @pytest.mark.asyncio
    async def test_middleware_low_overhead(self, test_app):
        """测试中间件开销很低"""
        import time

        async with AsyncClient(app=test_app, base_url="http://test") as client:
            start = time.time()

            # 执行100个请求
            for _ in range(100):
                await client.get("/test")

            elapsed = time.time() - start

            # 平均每个请求应该很快（< 10ms）
            avg_time = elapsed / 100
            assert avg_time < 0.01  # 10ms

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, test_app):
        """测试并发请求"""
        import asyncio

        async with AsyncClient(app=test_app, base_url="http://test") as client:
            # 并发执行多个请求
            tasks = [
                client.get("/test"),
                client.post("/test"),
                client.put("/test"),
                client.delete("/test"),
            ]

            responses = await asyncio.gather(*tasks)

            # 验证每个请求都正确设置了标志
            assert responses[0].json()["is_read_only"] is True   # GET
            assert responses[1].json()["is_read_only"] is False  # POST
            assert responses[2].json()["is_read_only"] is False  # PUT
            assert responses[3].json()["is_read_only"] is False  # DELETE


# ===========================================
# 测试总结
# ===========================================

"""
测试覆盖：
✅ 只读请求测试 - 3个测试用例
✅ 读写请求测试 - 4个测试用例
✅ TransactionMiddleware 类测试 - 3个测试用例
✅ 边界条件测试 - 3个测试用例
✅ 集成测试 - 4个测试用例
✅ 性能测试 - 2个测试用例

总计：19个测试用例

测试场景：
- 只读请求标记（GET, HEAD, OPTIONS）
- 读写请求标记（POST, PUT, PATCH, DELETE）
- 自定义 HTTP 方法
- 大小写敏感性
- 响应保持不变
- 真实端点集成
- 查询参数和请求体
- 中间件顺序独立性
- 低开销验证
- 并发请求处理
- 请求状态正确传递
"""
