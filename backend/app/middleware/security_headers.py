"""
安全头中间件
添加各种HTTP安全头，防止XSS、点击劫持等攻击
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全头中间件"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Content Security Policy - 防止XSS攻击
        if not settings.DEBUG:
            # 生产环境使用严格的CSP
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # TODO: 移除unsafe-*
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "media-src 'self' https:; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'none';"
            )
        
        # X-Content-Type-Options - 防止MIME类型嗅探
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-Frame-Options - 防止点击劫持
        response.headers["X-Frame-Options"] = "DENY"
        
        # X-XSS-Protection - XSS过滤器（虽然现代浏览器已弃用，但保留向后兼容）
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Strict-Transport-Security - 强制HTTPS（仅在生产环境）
        if settings.MINIO_SECURE:  # 如果使用HTTPS
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Referrer-Policy - 控制Referer信息
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions-Policy - 限制浏览器功能
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=()"
        )
        
        # X-Permitted-Cross-Domain-Policies - 限制跨域策略
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        
        return response


