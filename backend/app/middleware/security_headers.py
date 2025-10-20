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
        if settings.DEBUG:
            # 开发环境：允许 Vite 开发服务器工作
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' localhost:* http://localhost:*; "  # Vite HMR需要
                "style-src 'self' 'unsafe-inline'; "  # React inline styles
                "img-src 'self' data: https: http: blob:; "
                "font-src 'self' data:; "
                "connect-src 'self' ws: wss: http://localhost:* localhost:*; "  # WebSocket for HMR
                "media-src 'self' https: http: blob:; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'none'; "
                "upgrade-insecure-requests;"
            )
        else:
            # 生产环境：更严格的CSP，但允许必要的inline样式和CDN
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'sha256-{VITE_SCRIPT_HASH}'; "  # 使用脚本hash代替unsafe-inline
                "style-src 'self' 'unsafe-inline'; "  # 某些CSS-in-JS库需要
                "img-src 'self' data: https: blob:; "
                "font-src 'self' data: https:; "
                "connect-src 'self' https:; "
                "media-src 'self' https: blob:; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'none'; "
                "upgrade-insecure-requests;"
            )

        # X-Content-Type-Options - 防止MIME类型嗅探
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options - 防止点击劫持
        response.headers["X-Frame-Options"] = "DENY"

        # X-XSS-Protection - XSS过滤器（虽然现代浏览器已弃用，但保留向后兼容）
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Strict-Transport-Security - 强制HTTPS（仅在生产环境）
        if settings.MINIO_SECURE:  # 如果使用HTTPS
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # Referrer-Policy - 控制Referer信息
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy - 限制浏览器功能
        response.headers["Permissions-Policy"] = (
            "geolocation=(), " "microphone=(), " "camera=()"
        )

        # X-Permitted-Cross-Domain-Policies - 限制跨域策略
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"

        return response
