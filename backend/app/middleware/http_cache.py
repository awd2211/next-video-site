"""
HTTP缓存头中间件
为静态内容添加缓存控制头，减少不必要的服务器请求
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import Headers
import hashlib
from typing import Callable


class HTTPCacheMiddleware(BaseHTTPMiddleware):
    """HTTP缓存头中间件"""

    # 定义需要添加缓存头的路径和最大缓存时间（秒）
    CACHE_RULES = {
        "/api/v1/categories": 1800,  # 30分钟
        "/api/v1/countries": 3600,  # 1小时
        "/api/v1/tags": 1800,  # 30分钟
        "/api/v1/actors": 900,  # 15分钟
        "/api/v1/directors": 900,  # 15分钟
    }

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """处理请求并添加缓存头"""

        # 执行请求
        response = await call_next(request)

        # 只为GET请求添加缓存头
        if request.method != "GET":
            return response

        # 只为成功响应添加缓存头
        if response.status_code != 200:
            return response

        # 检查路径是否匹配缓存规则
        path = request.url.path
        for cache_path, max_age in self.CACHE_RULES.items():
            if path.startswith(cache_path):
                # 添加Cache-Control头
                response.headers["Cache-Control"] = (
                    f"public, max-age={max_age}"
                )

                # 对于列表接口，添加Vary头
                if "?" in str(request.url):
                    response.headers["Vary"] = "Accept, Accept-Encoding"

                break

        return response


def setup_http_cache():
    """设置HTTP缓存（供main.py调用）"""
    return HTTPCacheMiddleware

