import asyncio
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError, OperationalError

from app.admin import actors as admin_actors
from app.admin import admin_notifications
from app.admin import admin_payments
from app.admin import admin_coupons
from app.admin import admin_invoices
from app.admin import admin_subscriptions
from app.admin import subscription_plans as admin_subscription_plans
from app.admin import dashboard_config as admin_dashboard
from app.admin import ai_management as admin_ai
from app.admin import ai_logs as admin_ai_logs
from app.admin import oauth_management as admin_oauth
from app.admin import announcements as admin_announcements
from app.admin import banners as admin_banners
from app.admin import batch_operations as admin_batch
from app.admin import batch_upload as admin_batch_upload
from app.admin import categories as admin_categories
from app.admin import video_analytics as admin_video_analytics
from app.admin import comments as admin_comments
from app.admin import countries as admin_countries
from app.admin import danmaku as admin_danmaku
from app.admin import directors as admin_directors
from app.admin import email_config as admin_email
from app.admin import image_upload as admin_image_upload
from app.admin import ip_blacklist as admin_ip_blacklist
from app.admin import logs as admin_logs
from app.admin import media as admin_media
from app.admin import media_share as admin_media_share
from app.admin import media_version as admin_media_version
from app.admin import metrics as admin_metrics
from app.admin import operations as admin_operations
from app.admin import profile as admin_profile
from app.admin import rbac as admin_rbac
from app.admin import reports as admin_reports
from app.admin import scheduling as admin_scheduling
from app.admin import sentry_config as admin_sentry_config
from app.admin import series as admin_series
from app.admin import admin_seasons
from app.admin import admin_episodes
from app.admin import settings as admin_settings
from app.admin import settings_enhanced as admin_settings_enhanced
from app.admin import stats as admin_stats
from app.admin import subtitles as admin_subtitles
from app.admin import system_health as admin_system_health
from app.admin import tags as admin_tags
from app.admin import transcode as admin_transcode
from app.admin import two_factor as admin_two_factor
from app.admin import upload as admin_upload
from app.admin import users as admin_users
from app.admin import videos as admin_videos
from app.api import (
    actors,
    announcements,
    auth,
    captcha,
    categories,
    comments,
    danmaku,
    directors,
    favorite_folders,
    favorites,
    history,
    notifications,
    oauth,
    ratings,
    recommendations,
    search,
    sentry_config,
    series,
    share,
    shared_watchlist,
    shares,
    subtitles,
    users,
    videos,
    watchlist,
    websocket,
)
from app.api.v1 import (
    subscriptions,
    payments,
    invoices,
    coupons,
    webhooks,
)
from app.config import settings
from app.middleware.http_cache import HTTPCacheMiddleware
from app.middleware.operation_log import OperationLogMiddleware
from app.middleware.performance_monitor import PerformanceMonitorMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.request_size_limit import RequestSizeLimitMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.utils.rate_limit import limiter

# Rate limiter is imported from app.utils.rate_limit

app = FastAPI(
    title=settings.APP_NAME,
    description="Video streaming platform API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Rate limit error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]


# 数据库异常处理器
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """
    处理数据库完整性错误
    主要处理唯一约束和外键约束违反
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # 解析错误信息
    error_msg = str(exc.orig).lower()

    if "unique" in error_msg or "duplicate" in error_msg:
        # 唯一约束违反
        field = "resource"
        if "email" in error_msg:
            field = "email"
        elif "username" in error_msg:
            field = "username"
        elif "slug" in error_msg:
            field = "slug"

        logger.warning(
            f"Unique constraint violation: {field}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "field": field,
            },
        )

        return JSONResponse(
            status_code=409,
            content={
                "detail": f"A resource with this {field} already exists",
                "error_code": "DUPLICATE_RESOURCE",
                "request_id": request_id,
            },
        )

    elif "foreign key" in error_msg or "violates foreign key" in error_msg:
        # 外键约束违反
        logger.warning(
            "Foreign key constraint violation",
            extra={"request_id": request_id, "path": request.url.path},
        )

        return JSONResponse(
            status_code=400,
            content={
                "detail": "Referenced resource does not exist",
                "error_code": "INVALID_REFERENCE",
                "request_id": request_id,
            },
        )

    # 其他完整性错误
    logger.error("Database integrity error", exc_info=True, extra={"request_id": request_id})
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Database constraint violation",
            "error_code": "DATABASE_ERROR",
            "request_id": request_id,
        },
    )


@app.exception_handler(OperationalError)
async def operational_error_handler(request: Request, exc: OperationalError):
    """
    处理数据库操作错误
    通常是连接问题、超时等
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    logger.error(
        "Database operational error",
        exc_info=True,
        extra={
            "request_id": request_id,
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=503,
        content={
            "detail": "Database service temporarily unavailable, please try again later",
            "error_code": "SERVICE_UNAVAILABLE",
            "request_id": request_id,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理请求验证错误
    提供更友好的错误信息格式
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # 简化错误信息
    errors = []
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"][1:])  # 移除'body'或'query'
        errors.append(
            {
                "field": field_path or error["loc"][0],
                "message": error["msg"],
                "type": error["type"],
            }
        )

    logger.warning(
        "Request validation failed",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "errors": errors,
        },
    )

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Request validation failed",
            "error_code": "VALIDATION_ERROR",
            "errors": errors,
            "request_id": request_id,
        },
    )


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理器
    捕获所有未处理的异常，避免泄露敏感信息
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # 记录详细错误到日志
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "client": request.client.host if request.client else "unknown",
        },
    )

    # Log error to database and send notification
    try:
        from app.database import SessionLocal
        from app.utils.logging_utils import log_error
        from app.utils.admin_notification_service import AdminNotificationService
        import traceback

        db = SessionLocal()
        try:
            # Get user info if available
            user_id = None
            user_type = None
            if hasattr(request.state, "user"):
                user_id = request.state.user.id
                user_type = "admin" if getattr(request.state, "is_admin", False) else "user"

            # Get traceback
            tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
            traceback_str = ''.join(tb)

            # Determine error level
            level = "critical" if isinstance(exc, (SystemError, MemoryError, KeyboardInterrupt)) else "error"

            # Get status code
            status_code = getattr(exc, "status_code", 500)

            # Log to database
            error_log = await log_error(
                db=db,
                error_type=exc.__class__.__name__,
                error_message=str(exc),
                level=level,
                traceback_str=traceback_str,
                request=request,
                user_id=user_id,
                user_type=user_type,
                status_code=status_code,
            )

            # Send notification for critical/error level issues
            if level in ("critical", "error"):
                try:
                    await AdminNotificationService.notify_system_error(
                        db=db,
                        error_type=exc.__class__.__name__,
                        error_message=str(exc)[:200],  # Truncate to 200 chars
                        error_id=error_log.id if error_log else None,
                    )
                except Exception as notify_exc:
                    logger.error(f"Failed to send error notification: {notify_exc}")

        finally:
            await db.close()
    except Exception as log_exc:
        # If logging fails, log to console but don't break the app
        logger.error(f"Failed to log error to database: {log_exc}")

    # 根据DEBUG模式决定返回的错误详情
    if settings.DEBUG:
        # 开发环境：返回详细错误信息
        detail = str(exc)
    else:
        # 生产环境：返回通用错误信息
        detail = "Internal server error"

    return JSONResponse(
        status_code=500,
        content={
            "detail": detail,
            "error_code": "INTERNAL_ERROR",
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


# Request ID中间件（最先添加，为所有请求生成追踪ID）
app.add_middleware(RequestIDMiddleware)

# 性能监控中间件（记录慢API，阈值1秒）
app.add_middleware(PerformanceMonitorMiddleware, slow_threshold=1.0)

# 安全头中间件
app.add_middleware(SecurityHeadersMiddleware)

# HTTP缓存中间件（优化：减少不必要的请求）
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
    oauth.router, prefix=f"{settings.API_V1_PREFIX}", tags=["OAuth Authentication"]
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
    share.router, prefix=f"{settings.API_V1_PREFIX}", tags=["Public Share"]
)
app.include_router(
    series.router, prefix=f"{settings.API_V1_PREFIX}/series", tags=["Series"]
)
app.include_router(
    announcements.router,
    prefix=f"{settings.API_V1_PREFIX}/announcements",
    tags=["Announcements"],
)
app.include_router(
    watchlist.router,
    prefix=f"{settings.API_V1_PREFIX}/watchlist",
    tags=["Watchlist (My List)"],
)
app.include_router(
    shared_watchlist.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["Shared Watchlist"],
)
app.include_router(
    sentry_config.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["Public Sentry Config"],
)

# Payment and Subscription API routes
app.include_router(
    subscriptions.router,
    prefix=f"{settings.API_V1_PREFIX}/subscriptions",
    tags=["Subscriptions"],
)
app.include_router(
    payments.router,
    prefix=f"{settings.API_V1_PREFIX}/payments",
    tags=["Payments"],
)
app.include_router(
    invoices.router,
    prefix=f"{settings.API_V1_PREFIX}/invoices",
    tags=["Invoices"],
)
app.include_router(
    coupons.router,
    prefix=f"{settings.API_V1_PREFIX}/coupons",
    tags=["Coupons"],
)
app.include_router(
    webhooks.router,
    prefix=f"{settings.API_V1_PREFIX}/webhooks",
    tags=["Webhooks"],
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
    admin_settings_enhanced.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/system",
    tags=["Admin - System Settings Enhanced"],
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
    admin_seasons.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["Admin - Seasons"],
)
app.include_router(
    admin_episodes.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["Admin - Episodes"],
)
app.include_router(
    admin_image_upload.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/images",
    tags=["Admin - Images"],
)
app.include_router(
    admin_batch.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/batch",
    tags=["Admin - Batch Operations"],
)
app.include_router(
    admin_media.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["Admin - Media"],
)
app.include_router(
    admin_media_share.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["Admin - Media Share"],
)
app.include_router(
    admin_media_version.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["Admin - Media Version"],
)
app.include_router(
    admin_profile.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/profile",
    tags=["Admin - Profile"],
)
app.include_router(
    admin_two_factor.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/2fa",
    tags=["Admin - Two-Factor Authentication"],
)
app.include_router(
    admin_ai.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/ai",
    tags=["Admin - AI Management"],
)
app.include_router(
    admin_ai_logs.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/ai-logs",
    tags=["Admin - AI Logs & Monitoring"],
)
app.include_router(
    admin_system_health.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/system-health",
    tags=["Admin - System Health"],
)
app.include_router(
    admin_notifications.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/notifications",
    tags=["Admin - Notifications"],
)
app.include_router(
    admin_dashboard.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/dashboard",
    tags=["Admin - Dashboard Configuration"],
)
app.include_router(
    admin_batch_upload.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/upload",
    tags=["Admin - Batch Upload"],
)

# Admin Payment System routes
app.include_router(
    admin_subscription_plans.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/subscription-plans",
    tags=["Admin - Subscription Plans"],
)
app.include_router(
    admin_subscriptions.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/subscriptions",
    tags=["Admin - User Subscriptions"],
)
app.include_router(
    admin_payments.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/payments",
    tags=["Admin - Payments"],
)
app.include_router(
    admin_coupons.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/coupons",
    tags=["Admin - Coupons"],
)
app.include_router(
    admin_invoices.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/invoices",
    tags=["Admin - Invoices"],
)
app.include_router(
    admin_video_analytics.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/analytics",
    tags=["Admin - Video Analytics"],
)
app.include_router(
    admin_reports.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/reports",
    tags=["Admin - Reports"],
)
app.include_router(
    admin_scheduling.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["Admin - Content Scheduling"],
)
app.include_router(
    admin_oauth.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["Admin - OAuth Management"],
)
app.include_router(
    admin_rbac.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/rbac",
    tags=["Admin - RBAC (Role-Based Access Control)"],
)
app.include_router(
    admin_sentry_config.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["Admin - Sentry Configuration"],
)
app.include_router(
    admin_metrics.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["Admin - Performance Metrics"],
)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    # 🆕 验证配置（启动时检查）
    try:
        from app.utils.config_validator import validate_startup_config

        validate_startup_config()
    except SystemExit:
        # 配置验证失败，退出应用
        raise
    except Exception as e:
        logger.error(f"Configuration validation error: {e}")

    # 启用慢查询监控（仅在非DEBUG模式或需要时启用）
    if not settings.DEBUG or True:  # 可以通过环境变量控制
        from app.middleware.query_monitor import setup_query_monitoring

        setup_query_monitoring(threshold=0.5)  # 500ms阈值
        logger.info("Slow query monitoring enabled")

    # 启动存储监控（定期检查MinIO存储使用情况）
    try:
        from app.utils.storage_monitor import start_storage_monitoring

        # Start storage monitoring in background
        asyncio.create_task(start_storage_monitoring())
        logger.info("Storage monitoring started")
    except Exception as e:
        logger.error(f"Failed to start storage monitoring: {e}")


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
    from app.database import AsyncSessionLocal, get_pool_status
    from app.utils.cache import get_redis

    health_status = {"status": "healthy", "checks": {}, "version": "1.0.0"}

    # 检查数据库连接
    try:
        from sqlalchemy import select as sql_select

        async with AsyncSessionLocal() as db:
            await db.execute(sql_select(1))
        health_status["checks"]["database"] = "ok"

        # 🆕 添加连接池状态
        pool_status = get_pool_status()
        health_status["database_pool"] = pool_status

        # ⚠️ 连接池使用率过高警告
        usage_percent = (pool_status["checked_out"] / pool_status["total_connections"]) * 100
        if usage_percent > 80:
            health_status["warnings"] = health_status.get("warnings", [])
            health_status["warnings"].append(
                f"Database pool usage high: {usage_percent:.1f}%"
            )
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
        port=8000,
        reload=settings.DEBUG,
    )
