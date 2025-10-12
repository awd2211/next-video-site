"""
API性能监控中间件
自动记录响应时间超过阈值的API请求
"""
import time
from typing import Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class PerformanceMonitorMiddleware(BaseHTTPMiddleware):
    """API性能监控中间件"""

    def __init__(self, app, slow_threshold: float = 1.0):
        """
        初始化性能监控中间件

        Args:
            app: FastAPI应用
            slow_threshold: 慢API阈值（秒），默认1秒
        """
        super().__init__(app)
        self.slow_threshold = slow_threshold

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        记录API响应时间

        - 为所有响应添加X-Response-Time头
        - 记录超过阈值的慢API
        - 提供性能分析数据
        """
        start_time = time.time()

        # 执行请求
        response = await call_next(request)

        # 计算响应时间
        duration = time.time() - start_time

        # 添加响应时间头
        response.headers["X-Response-Time"] = f"{duration:.3f}s"

        # 记录慢API（仅记录成功的请求，避免错误日志重复）
        if duration > self.slow_threshold and 200 <= response.status_code < 300:
            request_id = getattr(request.state, "request_id", "unknown")

            logger.warning(
                f"Slow API: {request.method} {request.url.path} took {duration:.3f}s",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration": round(duration, 3),
                    "threshold": self.slow_threshold,
                    "query_params": dict(request.query_params),
                    "client": request.client.host if request.client else "unknown",
                    "request_id": request_id,
                    "status_code": response.status_code,
                },
            )

        return response
