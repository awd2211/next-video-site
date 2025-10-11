from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.middleware.operation_log import OperationLogMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.request_size_limit import RequestSizeLimitMiddleware
from app.utils.rate_limit import limiter
import logging
from app.api import (
    auth,
    videos,
    users,
    categories,
    search,
    comments,
    ratings,
    favorites,
    favorite_folders,
    history,
    actors,
    directors,
    captcha,
    recommendations,
    notifications,
    subtitles,
    websocket,
    danmaku,
    shares,
    series,
)
from app.admin import (
    videos as admin_videos,
    users as admin_users,
    comments as admin_comments,
    stats as admin_stats,
    settings as admin_settings,
    operations as admin_operations,
    logs as admin_logs,
    upload as admin_upload,
    email_config as admin_email,
    banners as admin_banners,
    announcements as admin_announcements,
    tags as admin_tags,
    countries as admin_countries,
    categories as admin_categories,
    actors as admin_actors,
    directors as admin_directors,
    transcode as admin_transcode,
    subtitles as admin_subtitles,
    danmaku as admin_danmaku,
    ip_blacklist as admin_ip_blacklist,
    series as admin_series,
    image_upload as admin_image_upload,
)

# Rate limiter is imported from app.utils.rate_limit
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="Video streaming platform API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Rate limit error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理器
    捕获所有未处理的异常，避免泄露敏感信息
    """
    # 记录详细错误到日志
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "client": request.client.host if request.client else "unknown",
        },
    )

    # 根据DEBUG模式决定返回的错误详情
    if settings.DEBUG:
        # 开发环境：返回详细错误信息
        detail = str(exc)
    else:
        # 生产环境：返回通用错误信息
        detail = "Internal server error"

    return JSONResponse(status_code=500, content={"detail": detail})


# 安全头中间件（最先添加）
app.add_middleware(SecurityHeadersMiddleware)

# HTTP缓存中间件（优化：减少不必要的请求）
from app.middleware.http_cache import HTTPCacheMiddleware

app.add_middleware(HTTPCacheMiddleware)

# 请求大小限制中间件
app.add_middleware(RequestSizeLimitMiddleware, max_size=10 * 1024 * 1024)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Operation log middleware (before routes)
app.add_middleware(OperationLogMiddleware)

# Public API routes
app.include_router(
    auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"]
)
app.include_router(
    captcha.router, prefix=f"{settings.API_V1_PREFIX}/captcha", tags=["Captcha"]
)
app.include_router(
    videos.router, prefix=f"{settings.API_V1_PREFIX}/videos", tags=["Videos"]
)
app.include_router(
    users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["Users"]
)
app.include_router(
    categories.router,
    prefix=f"{settings.API_V1_PREFIX}/categories",
    tags=["Categories"],
)
app.include_router(
    categories.countries_router,
    prefix=f"{settings.API_V1_PREFIX}/countries",
    tags=["Countries"],
)
app.include_router(
    categories.tags_router, prefix=f"{settings.API_V1_PREFIX}/tags", tags=["Tags"]
)
app.include_router(
    search.router, prefix=f"{settings.API_V1_PREFIX}/search", tags=["Search"]
)
app.include_router(
    comments.router, prefix=f"{settings.API_V1_PREFIX}/comments", tags=["Comments"]
)
app.include_router(
    ratings.router, prefix=f"{settings.API_V1_PREFIX}/ratings", tags=["Ratings"]
)
app.include_router(
    favorites.router, prefix=f"{settings.API_V1_PREFIX}/favorites", tags=["Favorites"]
)
app.include_router(
    favorite_folders.router,
    prefix=f"{settings.API_V1_PREFIX}/favorites",
    tags=["Favorite Folders"],
)
app.include_router(
    history.router, prefix=f"{settings.API_V1_PREFIX}/history", tags=["Watch History"]
)
app.include_router(
    actors.router, prefix=f"{settings.API_V1_PREFIX}/actors", tags=["Actors"]
)
app.include_router(
    directors.router, prefix=f"{settings.API_V1_PREFIX}/directors", tags=["Directors"]
)
app.include_router(
    recommendations.router,
    prefix=f"{settings.API_V1_PREFIX}/recommendations",
    tags=["Recommendations"],
)
app.include_router(
    notifications.router,
    prefix=f"{settings.API_V1_PREFIX}/notifications",
    tags=["Notifications"],
)
app.include_router(
    subtitles.router, prefix=f"{settings.API_V1_PREFIX}/videos", tags=["Subtitles"]
)
app.include_router(
    websocket.router, prefix=f"{settings.API_V1_PREFIX}", tags=["WebSocket"]
)
app.include_router(
    danmaku.router, prefix=f"{settings.API_V1_PREFIX}/danmaku", tags=["Danmaku"]
)
app.include_router(
    shares.router, prefix=f"{settings.API_V1_PREFIX}/shares", tags=["Shares"]
)
app.include_router(
    series.router, prefix=f"{settings.API_V1_PREFIX}/series", tags=["Series"]
)

# Admin API routes
app.include_router(
    admin_videos.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/videos",
    tags=["Admin - Videos"],
)
app.include_router(
    admin_users.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/users",
    tags=["Admin - Users"],
)
app.include_router(
    admin_comments.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/comments",
    tags=["Admin - Comments"],
)
app.include_router(
    admin_stats.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/stats",
    tags=["Admin - Statistics"],
)
app.include_router(
    admin_settings.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/system",
    tags=["Admin - System Settings"],
)
app.include_router(
    admin_operations.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/operations",
    tags=["Admin - Operations"],
)
app.include_router(
    admin_logs.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/logs",
    tags=["Admin - Logs"],
)
app.include_router(
    admin_upload.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/upload",
    tags=["Admin - Upload"],
)
app.include_router(
    admin_email.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/email",
    tags=["Admin - Email"],
)
app.include_router(
    admin_banners.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/banners",
    tags=["Admin - Banners"],
)
app.include_router(
    admin_announcements.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/announcements",
    tags=["Admin - Announcements"],
)
app.include_router(
    admin_tags.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/tags",
    tags=["Admin - Tags"],
)
app.include_router(
    admin_countries.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/countries",
    tags=["Admin - Countries"],
)
app.include_router(
    admin_categories.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/categories",
    tags=["Admin - Categories"],
)
app.include_router(
    admin_actors.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/actors",
    tags=["Admin - Actors"],
)
app.include_router(
    admin_directors.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/directors",
    tags=["Admin - Directors"],
)
app.include_router(
    admin_transcode.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["Admin - Transcode"],
)
app.include_router(
    admin_subtitles.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["Admin - Subtitles"],
)
app.include_router(
    admin_danmaku.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/danmaku",
    tags=["Admin - Danmaku"],
)
app.include_router(
    admin_ip_blacklist.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/ip-blacklist",
    tags=["Admin - IP Blacklist"],
)
app.include_router(
    admin_series.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/series",
    tags=["Admin - Series"],
)
app.include_router(
    admin_image_upload.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/images",
    tags=["Admin - Images"],
)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    # 启用慢查询监控（仅在非DEBUG模式或需要时启用）
    if not settings.DEBUG or True:  # 可以通过环境变量控制
        from app.middleware.query_monitor import setup_query_monitoring

        setup_query_monitoring(threshold=0.5)  # 500ms阈值
        logger.info("Slow query monitoring enabled")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to VideoSite API",
        "version": "1.0.0",
        "docs": "/api/docs",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    检查应用和依赖服务的健康状态
    """
    from app.database import AsyncSessionLocal
    from app.utils.cache import get_redis

    health_status = {"status": "healthy", "checks": {}, "version": "1.0.0"}

    # 检查数据库连接
    try:
        from sqlalchemy import select as sql_select

        async with AsyncSessionLocal() as db:
            await db.execute(sql_select(1))
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {type(e).__name__}"
        health_status["status"] = "unhealthy"
        logger.error(f"Database health check failed: {e}")

    # 检查Redis连接
    try:
        redis_client = await get_redis()
        await redis_client.ping()
        health_status["checks"]["redis"] = "ok"
    except Exception as e:
        health_status["checks"]["redis"] = f"error: {type(e).__name__}"
        health_status["status"] = "unhealthy"
        logger.error(f"Redis health check failed: {e}")

    # 如果任何检查失败，返回503状态码
    status_code = 200 if health_status["status"] == "healthy" else 503

    return JSONResponse(status_code=status_code, content=health_status)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG,
    )
