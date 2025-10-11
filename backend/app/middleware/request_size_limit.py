"""
请求大小限制中间件
防止过大的请求导致的DoS攻击
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


# 默认最大请求大小（10MB）
# 上传接口应该单独处理
DEFAULT_MAX_REQUEST_SIZE = 10 * 1024 * 1024


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """请求大小限制中间件"""
    
    def __init__(self, app, max_size: int = DEFAULT_MAX_REQUEST_SIZE):
        super().__init__(app)
        self.max_size = max_size
        # 上传路径白名单（这些路径允许更大的请求）
        self.upload_paths = [
            "/api/v1/admin/upload",
            "/api/v1/admin/videos",
            "/api/v1/admin/images",
            "/api/v1/admin/subtitles",
        ]
    
    async def dispatch(self, request: Request, call_next):
        # 检查是否是上传路径
        is_upload_path = any(request.url.path.startswith(path) for path in self.upload_paths)
        
        # 非上传路径检查请求大小
        if not is_upload_path and request.method in ["POST", "PUT", "PATCH"]:
            content_length = request.headers.get("content-length")
            
            if content_length:
                try:
                    content_length_int = int(content_length)
                    if content_length_int > self.max_size:
                        raise HTTPException(
                            status_code=413,
                            detail=f"请求体过大，最大允许 {self.max_size // (1024*1024)}MB"
                        )
                except ValueError:
                    # content-length不是有效整数
                    raise HTTPException(
                        status_code=400,
                        detail="无效的Content-Length头"
                    )
        
        response = await call_next(request)
        return response


