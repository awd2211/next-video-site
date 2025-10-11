"""
事务管理中间件
区分只读和读写操作，优化事务管理
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class TransactionMiddleware(BaseHTTPMiddleware):
    """
    事务管理中间件

    优化策略：
    - GET请求：只读操作，不需要commit
    - POST/PUT/PATCH/DELETE：读写操作，需要commit
    """

    # 只读方法列表
    READ_ONLY_METHODS = {"GET", "HEAD", "OPTIONS"}

    async def dispatch(self, request: Request, call_next):
        """
        根据HTTP方法自动处理事务

        注意：实际的事务管理由database.py的get_db()依赖处理
        这个中间件主要用于设置标记，供依赖使用
        """
        # 标记请求类型
        if request.method in self.READ_ONLY_METHODS:
            request.state.is_read_only = True
        else:
            request.state.is_read_only = False

        response = await call_next(request)
        return response
