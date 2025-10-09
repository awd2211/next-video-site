from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.middleware.operation_log import OperationLogMiddleware
from app.api import auth, videos, users, categories, search
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
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

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
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(videos.router, prefix=f"{settings.API_V1_PREFIX}/videos", tags=["Videos"])
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["Users"])
app.include_router(categories.router, prefix=f"{settings.API_V1_PREFIX}/categories", tags=["Categories"])
app.include_router(categories.countries_router, prefix=f"{settings.API_V1_PREFIX}/countries", tags=["Countries"])
app.include_router(categories.tags_router, prefix=f"{settings.API_V1_PREFIX}/tags", tags=["Tags"])
app.include_router(search.router, prefix=f"{settings.API_V1_PREFIX}/search", tags=["Search"])

# Admin API routes
app.include_router(admin_videos.router, prefix=f"{settings.API_V1_PREFIX}/admin/videos", tags=["Admin - Videos"])
app.include_router(admin_users.router, prefix=f"{settings.API_V1_PREFIX}/admin/users", tags=["Admin - Users"])
app.include_router(admin_comments.router, prefix=f"{settings.API_V1_PREFIX}/admin/comments", tags=["Admin - Comments"])
app.include_router(admin_stats.router, prefix=f"{settings.API_V1_PREFIX}/admin/stats", tags=["Admin - Statistics"])
app.include_router(admin_settings.router, prefix=f"{settings.API_V1_PREFIX}/admin/system", tags=["Admin - System Settings"])
app.include_router(admin_operations.router, prefix=f"{settings.API_V1_PREFIX}/admin/operations", tags=["Admin - Operations"])
app.include_router(admin_logs.router, prefix=f"{settings.API_V1_PREFIX}/admin/logs", tags=["Admin - Logs"])
app.include_router(admin_upload.router, prefix=f"{settings.API_V1_PREFIX}/admin/upload", tags=["Admin - Upload"])
app.include_router(admin_email.router, prefix=f"{settings.API_V1_PREFIX}/admin/email", tags=["Admin - Email"])
app.include_router(admin_banners.router, prefix=f"{settings.API_V1_PREFIX}/admin/banners", tags=["Admin - Banners"])
app.include_router(admin_announcements.router, prefix=f"{settings.API_V1_PREFIX}/admin/announcements", tags=["Admin - Announcements"])


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
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
