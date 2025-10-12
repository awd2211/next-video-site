"""
请求ID中间件
为每个请求添加唯一ID，便于追踪和调试
"""
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    """请求ID中间件"""

    async def dispatch(self, request: Request, call_next):
        """
        为每个请求添加唯一ID

        - 客户端可以通过X-Request-ID头传递ID
        - 如果没有提供，自动生成UUID
        - ID会添加到响应头，便于客户端追踪
        - ID存储在request.state，供日志使用
        """
        # 生成或使用客户端提供的request_id
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # 存储到request.state，供后续使用（日志、错误处理等）
        request.state.request_id = request_id

        # 执行请求
        response = await call_next(request)

        # 添加到响应头，便于客户端追踪
        response.headers["X-Request-ID"] = request_id

        return response
