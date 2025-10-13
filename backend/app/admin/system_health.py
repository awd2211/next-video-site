"""
System Health Monitoring API
Provides real-time system health metrics for admin dashboard
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
import psutil
import time
from datetime import datetime, timedelta
import json
from loguru import logger
import sys
import platform

from app.database import get_db, get_pool_status
from app.utils.dependencies import get_current_admin_user
from app.utils.cache import get_redis
from app.utils.minio_client import minio_client
from app.models.user import AdminUser

router = APIRouter()

# Cache key prefix for health metrics
HEALTH_CACHE_PREFIX = "system:health:"
METRICS_HISTORY_KEY = "system:metrics:history"
CACHE_TTL = 5  # seconds

# Store application start time
APP_START_TIME = datetime.utcnow()


async def check_database_health(db: AsyncSession) -> Dict[str, Any]:
    """Check database connection and pool status"""
    try:
        # Test query
        start = time.time()
        await db.execute("SELECT 1")
        query_time = (time.time() - start) * 1000  # ms

        # Get pool status
        pool_status = get_pool_status()

        # Calculate pool utilization
        total_connections = pool_status['pool_size'] + pool_status['overflow']
        used_connections = pool_status['checked_out']
        utilization = (used_connections / total_connections * 100) if total_connections > 0 else 0

        return {
            "status": "healthy" if query_time < 100 else "degraded",
            "response_time_ms": round(query_time, 2),
            "pool_size": pool_status['pool_size'],
            "checked_out": pool_status['checked_out'],
            "checked_in": pool_status['checked_in'],
            "overflow": pool_status['overflow'],
            "utilization_percent": round(utilization, 1),
            "message": "Database connection healthy" if query_time < 100 else "Slow database response"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Database connection failed"
        }


async def check_redis_health() -> Dict[str, Any]:
    """Check Redis connection and memory usage"""
    try:
        redis_client = await get_redis()

        # Test ping
        start = time.time()
        await redis_client.ping()
        ping_time = (time.time() - start) * 1000  # ms

        # Get memory info
        info = await redis_client.info('memory')
        used_memory_mb = info.get('used_memory', 0) / (1024 * 1024)
        max_memory_mb = info.get('maxmemory', 0) / (1024 * 1024)

        # Get key count
        dbsize = await redis_client.dbsize()

        # Memory utilization
        memory_utilization = (used_memory_mb / max_memory_mb * 100) if max_memory_mb > 0 else 0

        return {
            "status": "healthy" if ping_time < 50 else "degraded",
            "response_time_ms": round(ping_time, 2),
            "used_memory_mb": round(used_memory_mb, 2),
            "max_memory_mb": round(max_memory_mb, 2) if max_memory_mb > 0 else "unlimited",
            "memory_utilization_percent": round(memory_utilization, 1) if max_memory_mb > 0 else None,
            "keys_count": dbsize,
            "message": "Redis connection healthy" if ping_time < 50 else "Slow Redis response"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Redis connection failed"
        }


async def check_minio_health() -> Dict[str, Any]:
    """Check MinIO/S3 storage availability"""
    try:
        # minio_client is already imported as a singleton instance

        start = time.time()
        # Check if bucket exists
        bucket_exists = minio_client.bucket_exists("videos")
        response_time = (time.time() - start) * 1000  # ms

        # Try to get bucket stats (this may not be available on all MinIO versions)
        try:
            # List objects to verify read access
            objects = list(minio_client.list_objects("videos", max_keys=1))
            can_read = True
        except:
            can_read = False

        return {
            "status": "healthy" if bucket_exists and response_time < 200 else "degraded",
            "response_time_ms": round(response_time, 2),
            "bucket_exists": bucket_exists,
            "can_read": can_read,
            "message": "Storage service healthy" if bucket_exists else "Storage bucket not found"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Storage service unavailable"
        }


def get_system_resources() -> Dict[str, Any]:
    """Get system CPU and memory usage"""
    try:
        # CPU usage (non-blocking, use cached value)
        cpu_percent = psutil.cpu_percent(interval=0)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        cpu_freq_current = cpu_freq.current if cpu_freq else None

        # Memory usage
        memory = psutil.virtual_memory()
        memory_used_gb = memory.used / (1024 ** 3)
        memory_total_gb = memory.total / (1024 ** 3)
        memory_percent = memory.percent

        # Disk usage
        disk = psutil.disk_usage('/')
        disk_used_gb = disk.used / (1024 ** 3)
        disk_total_gb = disk.total / (1024 ** 3)
        disk_percent = disk.percent

        # Network IO stats
        net_io = psutil.net_io_counters()
        bytes_sent_gb = net_io.bytes_sent / (1024 ** 3)
        bytes_recv_gb = net_io.bytes_recv / (1024 ** 3)

        # Process info
        process_count = len(psutil.pids())

        return {
            "cpu": {
                "usage_percent": round(cpu_percent, 1),
                "cores": cpu_count,
                "frequency_mhz": round(cpu_freq_current, 1) if cpu_freq_current else None,
                "status": "healthy" if cpu_percent < 70 else "warning" if cpu_percent < 90 else "critical"
            },
            "memory": {
                "used_gb": round(memory_used_gb, 2),
                "total_gb": round(memory_total_gb, 2),
                "usage_percent": round(memory_percent, 1),
                "available_gb": round(memory.available / (1024 ** 3), 2),
                "status": "healthy" if memory_percent < 80 else "warning" if memory_percent < 95 else "critical"
            },
            "disk": {
                "used_gb": round(disk_used_gb, 2),
                "total_gb": round(disk_total_gb, 2),
                "free_gb": round(disk.free / (1024 ** 3), 2),
                "usage_percent": round(disk_percent, 1),
                "status": "healthy" if disk_percent < 80 else "warning" if disk_percent < 95 else "critical"
            },
            "network": {
                "bytes_sent_gb": round(bytes_sent_gb, 2),
                "bytes_recv_gb": round(bytes_recv_gb, 2),
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errors_in": net_io.errin,
                "errors_out": net_io.errout,
                "drops_in": net_io.dropin,
                "drops_out": net_io.dropout
            },
            "processes": {
                "count": process_count
            }
        }
    except Exception as e:
        logger.error(f"Failed to get system resources: {e}")
        return {
            "error": str(e),
            "message": "Failed to get system resources"
        }


async def store_metrics_history(redis_client, metrics: Dict[str, Any]):
    """Store metrics in history for trend analysis"""
    try:
        # Store in a list with timestamp
        history_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "data": metrics
        }

        # Add to list (keep last 100 entries, ~8 minutes at 5s interval)
        await redis_client.lpush(METRICS_HISTORY_KEY, json.dumps(history_entry))
        await redis_client.ltrim(METRICS_HISTORY_KEY, 0, 99)
        await redis_client.expire(METRICS_HISTORY_KEY, 600)  # 10 minutes
    except Exception as e:
        logger.warning(f"Failed to store metrics history: {e}")


@router.get("/health")
async def get_system_health(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
    use_cache: bool = Query(True, description="Use cached data if available")
):
    """
    Get comprehensive system health status

    Returns:
    - Database health and pool status
    - Redis health and memory usage
    - MinIO/S3 storage health
    - System CPU, memory, disk, network usage
    - Overall health status
    """
    redis_client = await get_redis()
    cache_key = f"{HEALTH_CACHE_PREFIX}status"

    # Try to get from cache
    if use_cache:
        try:
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                logger.debug("Returning cached health status")
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache read failed: {e}")

    # Check all services
    database = await check_database_health(db)
    redis = await check_redis_health()
    storage = await check_minio_health()
    system = get_system_resources()

    # Calculate overall health
    service_statuses = [
        database.get('status'),
        redis.get('status'),
        storage.get('status')
    ]

    if all(s == 'healthy' for s in service_statuses):
        overall_status = 'healthy'
    elif any(s == 'unhealthy' for s in service_statuses):
        overall_status = 'unhealthy'
    else:
        overall_status = 'degraded'

    response = {
        "timestamp": datetime.utcnow().isoformat(),
        "overall_status": overall_status,
        "services": {
            "database": database,
            "redis": redis,
            "storage": storage
        },
        "system_resources": system
    }

    # Cache the response
    try:
        await redis_client.setex(cache_key, CACHE_TTL, json.dumps(response))

        # Store in history for trends
        metrics_for_history = {
            "cpu_usage": system.get("cpu", {}).get("usage_percent", 0),
            "memory_usage": system.get("memory", {}).get("usage_percent", 0),
            "disk_usage": system.get("disk", {}).get("usage_percent", 0),
            "db_response_time": database.get("response_time_ms", 0),
            "redis_response_time": redis.get("response_time_ms", 0),
            "storage_response_time": storage.get("response_time_ms", 0)
        }
        await store_metrics_history(redis_client, metrics_for_history)
    except Exception as e:
        logger.warning(f"Cache write failed: {e}")

    return response


@router.get("/metrics")
async def get_system_metrics(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
    use_cache: bool = Query(True, description="Use cached data if available")
):
    """
    Get detailed system metrics for monitoring

    Returns time-series data and statistics
    """
    from sqlalchemy import func, select as sql_select
    from app.models.video import Video
    from app.models.user import User
    from app.models.comment import Comment

    redis_client = await get_redis()
    cache_key = f"{HEALTH_CACHE_PREFIX}metrics"

    # Try to get from cache
    if use_cache:
        try:
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                logger.debug("Returning cached metrics")
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Metrics cache read failed: {e}")

    # Get database statistics
    video_count = await db.scalar(sql_select(func.count(Video.id)))
    user_count = await db.scalar(sql_select(func.count(User.id)))
    comment_count = await db.scalar(sql_select(func.count(Comment.id)))

    # Get recent activity (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)

    new_videos_24h = await db.scalar(
        sql_select(func.count(Video.id)).where(Video.created_at >= yesterday)
    )
    new_users_24h = await db.scalar(
        sql_select(func.count(User.id)).where(User.created_at >= yesterday)
    )
    new_comments_24h = await db.scalar(
        sql_select(func.count(Comment.id)).where(Comment.created_at >= yesterday)
    )

    response = {
        "timestamp": datetime.utcnow().isoformat(),
        "database": {
            "total_videos": video_count or 0,
            "total_users": user_count or 0,
            "total_comments": comment_count or 0,
            "new_videos_24h": new_videos_24h or 0,
            "new_users_24h": new_users_24h or 0,
            "new_comments_24h": new_comments_24h or 0
        }
    }

    # Cache the response (longer TTL for metrics)
    try:
        await redis_client.setex(cache_key, 30, json.dumps(response))
    except Exception as e:
        logger.warning(f"Metrics cache write failed: {e}")

    return response


@router.get("/history")
async def get_metrics_history(
    current_admin: AdminUser = Depends(get_current_admin_user),
    limit: int = Query(50, ge=1, le=100, description="Number of history entries to return")
):
    """
    Get historical metrics for trend charts

    Returns last N metrics entries with timestamps
    """
    try:
        redis_client = await get_redis()

        # Get history from Redis list
        history_data = await redis_client.lrange(METRICS_HISTORY_KEY, 0, limit - 1)

        if not history_data:
            return {
                "count": 0,
                "history": []
            }

        # Parse JSON entries
        parsed_history = []
        for entry in history_data:
            try:
                parsed = json.loads(entry)
                parsed_history.append(parsed)
            except json.JSONDecodeError:
                logger.warning("Failed to parse history entry")
                continue

        # Reverse to get chronological order (oldest first)
        parsed_history.reverse()

        return {
            "count": len(parsed_history),
            "history": parsed_history
        }

    except Exception as e:
        logger.error(f"Failed to get metrics history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics history")


@router.get("/info")
async def get_system_info(
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Get detailed system information
    
    Returns:
    - Server hostname and platform info
    - Python version and packages
    - Application uptime
    - System uptime
    """
    try:
        # System boot time
        system_boot_time = datetime.fromtimestamp(psutil.boot_time())
        system_uptime_seconds = (datetime.now() - system_boot_time).total_seconds()
        
        # Application uptime
        app_uptime_seconds = (datetime.utcnow() - APP_START_TIME).total_seconds()
        
        # Platform info
        uname = platform.uname()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "server": {
                "hostname": platform.node(),
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor() or uname.processor
            },
            "python": {
                "version": sys.version,
                "version_info": {
                    "major": sys.version_info.major,
                    "minor": sys.version_info.minor,
                    "micro": sys.version_info.micro
                },
                "implementation": platform.python_implementation(),
                "compiler": platform.python_compiler()
            },
            "application": {
                "start_time": APP_START_TIME.isoformat(),
                "uptime_seconds": round(app_uptime_seconds),
                "uptime_formatted": format_uptime(app_uptime_seconds)
            },
            "system": {
                "boot_time": system_boot_time.isoformat(),
                "uptime_seconds": round(system_uptime_seconds),
                "uptime_formatted": format_uptime(system_uptime_seconds)
            }
        }
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system information")


def format_uptime(seconds: float) -> str:
    """Format uptime in human-readable format"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return " ".join(parts)
