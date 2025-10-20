"""
System Health Monitoring API
Provides real-time system health metrics for admin dashboard
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any, Optional, List
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
from app.services.alert_service import AlertService, save_metrics_to_database
from app.services.sla_service import SLAService, generate_hourly_sla, generate_daily_sla
from app.utils.celery_monitor import CeleryMonitor

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
        await db.execute(text("SELECT 1"))
        query_time = (time.time() - start) * 1000  # ms

        # Get database name
        result = await db.execute(text("SELECT current_database()"))
        db_name = result.scalar()

        # Get database version
        version_result = await db.execute(text("SELECT version()"))
        db_version = version_result.scalar()
        # Extract just the version number (e.g., "PostgreSQL 14.5")
        db_version_short = ' '.join(db_version.split()[:2]) if db_version else "Unknown"

        # Get pool status
        pool_status = get_pool_status()

        # Calculate pool utilization
        # Use pool_size as base (fixed size), overflow is dynamic and can be negative
        pool_size = pool_status['pool_size']
        checked_out = pool_status['checked_out']
        overflow = pool_status['overflow']

        # Total active connections = checked_out (which includes overflow if any)
        # Utilization = checked_out / pool_size * 100
        # Note: can exceed 100% when using overflow connections
        utilization = (checked_out / pool_size * 100) if pool_size > 0 else 0

        return {
            "status": "healthy" if query_time < 100 else "degraded",
            "response_time_ms": round(query_time, 2),
            "database_name": db_name,
            "database_version": db_version_short,
            "pool_size": pool_status['pool_size'],
            "checked_out": checked_out,
            "checked_in": pool_status['checked_in'],
            "overflow": max(0, overflow),  # Ensure overflow is non-negative for display
            "utilization_percent": round(utilization, 1),
            "message": f"Database '{db_name}' healthy" if query_time < 100 else "Slow database response"
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
    """Check MinIO/S3 storage availability and usage"""
    try:
        # minio_client is already imported as a singleton instance

        start = time.time()

        # List all buckets
        buckets = minio_client.client.list_buckets()
        bucket_list = []
        total_objects = 0
        total_size_gb = 0.0

        for bucket in buckets:
            try:
                # Get objects in this bucket
                objects = list(minio_client.client.list_objects(bucket.name, recursive=True))
                bucket_size = sum(obj.size for obj in objects)
                bucket_size_gb = bucket_size / (1024 ** 3)

                bucket_info = {
                    "name": bucket.name,
                    "creation_date": bucket.creation_date.isoformat() if bucket.creation_date else None,
                    "object_count": len(objects),
                    "size_gb": round(bucket_size_gb, 3),
                    "size_bytes": bucket_size,
                }
                bucket_list.append(bucket_info)

                total_objects += len(objects)
                total_size_gb += bucket_size_gb

            except Exception as e:
                logger.debug(f"Failed to get stats for bucket {bucket.name}: {e}")
                bucket_list.append({
                    "name": bucket.name,
                    "creation_date": bucket.creation_date.isoformat() if bucket.creation_date else None,
                    "error": str(e)
                })

        response_time = (time.time() - start) * 1000  # ms

        # Check if default bucket exists
        bucket_exists = minio_client.client.bucket_exists(minio_client.bucket_name)

        # Try to verify read access on default bucket
        can_read = False
        try:
            objects = minio_client.client.list_objects(minio_client.bucket_name)
            try:
                next(iter(objects))
            except StopIteration:
                pass
            can_read = True
        except Exception as e:
            logger.debug(f"MinIO read check failed: {e}")

        # Build response
        response = {
            "status": "healthy" if bucket_exists and response_time < 200 else "degraded",
            "response_time_ms": round(response_time, 2),
            "bucket_exists": bucket_exists,
            "can_read": can_read,
            "buckets": bucket_list,
            "buckets_count": len(bucket_list),
            "used_gb": round(total_size_gb, 2),
            "object_count": total_objects,
            "total_gb": 1000.0,  # Default 1TB, can be made configurable
            "utilization_percent": round((total_size_gb / 1000.0) * 100, 2),
            "message": f"Storage service healthy - {len(bucket_list)} bucket(s)" if bucket_exists else "Storage bucket not found"
        }

        return response

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Storage service unavailable"
        }


def check_celery_health() -> Dict[str, Any]:
    """Check Celery task queue health"""
    try:
        # 获取Celery健康状态
        health_check = CeleryMonitor.check_health()

        if not health_check.get("healthy"):
            return {
                "status": "unhealthy",
                "workers_count": 0,
                "active_tasks": 0,
                "message": health_check.get("message", "Celery workers not available")
            }

        # 获取队列统计
        queue_stats = CeleryMonitor.get_queue_stats()

        if queue_stats.get("status") == "error":
            return {
                "status": "unhealthy",
                "workers_count": 0,
                "active_tasks": 0,
                "message": queue_stats.get("message", "Failed to get queue stats")
            }

        # 获取任务统计（成功/失败）
        task_stats = CeleryMonitor.get_task_stats()

        active_tasks = queue_stats.get("active_tasks", 0)
        workers_count = queue_stats.get("workers_count", 0)

        # 判断状态
        if workers_count == 0:
            status = "unhealthy"
            message = "No Celery workers available"
        elif active_tasks > 100:
            status = "warning"
            message = f"High task backlog: {active_tasks} active tasks"
        else:
            status = "healthy"
            message = "Celery task queue healthy"

        return {
            "status": status,
            "workers_count": workers_count,
            "active_tasks": active_tasks,
            "reserved_tasks": queue_stats.get("reserved_tasks", 0),
            "scheduled_tasks": queue_stats.get("scheduled_tasks", 0),
            "total_succeeded": task_stats.get("total_succeeded", 0),
            "total_failed": task_stats.get("total_failed", 0),
            "active_task_list": queue_stats.get("active_task_list", []),
            "reserved_task_list": queue_stats.get("reserved_task_list", []),
            "registered_tasks": queue_stats.get("registered_tasks", []),
            "message": message
        }

    except Exception as e:
        logger.error(f"Celery health check failed: {e}")
        return {
            "status": "unhealthy",
            "workers_count": 0,
            "active_tasks": 0,
            "error": str(e),
            "message": "Celery service unavailable"
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
    celery = check_celery_health()
    system = get_system_resources()

    # Calculate overall health
    service_statuses = [
        database.get('status'),
        redis.get('status'),
        storage.get('status'),
        celery.get('status')
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
            "storage": storage,
            "celery": celery
        },
        "system_resources": system
    }

    # 保存指标到数据库并检查告警
    try:
        # 保存指标到数据库
        await save_metrics_to_database(db, response)

        # 检查并创建告警
        alert_service = AlertService(db)
        new_alerts = await alert_service.check_and_create_alerts(response)

        # 获取告警统计
        alert_stats = await alert_service.get_alert_statistics()

        # 添加告警信息到响应
        response["alerts"] = {
            "statistics": alert_stats,
            "new_alerts_count": len(new_alerts)
        }

    except Exception as e:
        logger.error(f"Failed to save metrics or check alerts: {e}")

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


# ============ Alert Management Endpoints ============


@router.get("/alerts")
async def get_alerts(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
    status: str = Query("active", description="Alert status filter (active/resolved/all)"),
    alert_type: Optional[str] = Query(None, description="Alert type filter"),
    severity: Optional[str] = Query(None, description="Severity filter (critical/warning)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size")
):
    """
    获取告警列表

    支持按状态、类型、严重程度过滤和分页
    """
    from sqlalchemy import and_, or_
    from app.models.system_metrics import SystemAlert

    try:
        # 构建查询条件
        conditions = []

        if status != "all":
            conditions.append(SystemAlert.status == status)

        if alert_type:
            conditions.append(SystemAlert.alert_type == alert_type)

        if severity:
            conditions.append(SystemAlert.severity == severity)

        # 查询总数
        from sqlalchemy import func, select as sql_select
        count_stmt = sql_select(func.count(SystemAlert.id))
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))

        total = await db.scalar(count_stmt)

        # 查询数据
        stmt = sql_select(SystemAlert)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(
            SystemAlert.severity.desc(),
            SystemAlert.triggered_at.desc()
        ).offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(stmt)
        alerts = result.scalars().all()

        # 转换为字典格式
        alert_list = []
        for alert in alerts:
            alert_list.append({
                "id": alert.id,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "title": alert.title,
                "message": alert.message,
                "metric_name": alert.metric_name,
                "metric_value": alert.metric_value,
                "threshold_value": alert.threshold_value,
                "status": alert.status,
                "triggered_at": alert.triggered_at.isoformat(),
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                "acknowledged_by": alert.acknowledged_by,
                "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                "notes": alert.notes,
                "context": alert.context,
                "created_at": alert.created_at.isoformat(),
                "updated_at": alert.updated_at.isoformat() if alert.updated_at else None
            })

        return {
            "items": alert_list,
            "total": total or 0,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size if total else 0
        }

    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alerts")


@router.get("/alerts/statistics")
async def get_alert_statistics(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """
    获取告警统计信息

    返回活跃告警数、严重告警数、警告数等统计数据
    """
    try:
        alert_service = AlertService(db)
        stats = await alert_service.get_alert_statistics()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "statistics": stats
        }

    except Exception as e:
        logger.error(f"Failed to get alert statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alert statistics")


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
    notes: Optional[str] = Query(None, description="处理备注")
):
    """
    确认告警

    管理员确认已知晓该告警并正在处理
    """
    try:
        alert_service = AlertService(db)
        alert = await alert_service.acknowledge_alert(
            alert_id=alert_id,
            admin_user_id=current_admin.id,
            notes=notes
        )

        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        return {
            "success": True,
            "message": "Alert acknowledged successfully",
            "alert": {
                "id": alert.id,
                "title": alert.title,
                "acknowledged_by": alert.acknowledged_by,
                "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                "notes": alert.notes
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to acknowledge alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to acknowledge alert")


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
    notes: Optional[str] = Query(None, description="解决备注")
):
    """
    手动解决告警

    管理员手动将告警标记为已解决
    """
    try:
        from sqlalchemy import select as sql_select
        from app.models.system_metrics import SystemAlert

        stmt = sql_select(SystemAlert).where(SystemAlert.id == alert_id)
        result = await db.execute(stmt)
        alert = result.scalar_one_or_none()

        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        alert.status = "resolved"
        alert.resolved_at = datetime.utcnow()
        alert.updated_at = datetime.utcnow()

        if notes:
            alert.notes = notes if not alert.notes else f"{alert.notes}\n解决备注: {notes}"

        await db.commit()
        await db.refresh(alert)

        return {
            "success": True,
            "message": "Alert resolved successfully",
            "alert": {
                "id": alert.id,
                "title": alert.title,
                "status": alert.status,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                "notes": alert.notes
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve alert: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to resolve alert")


@router.get("/alerts/active/count")
async def get_active_alerts_count(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """
    获取活跃告警数量（快速接口）

    用于前端显示告警徽章数量
    """
    try:
        from sqlalchemy import and_, func, select as sql_select
        from app.models.system_metrics import SystemAlert

        # 总活跃告警数
        total_stmt = sql_select(func.count(SystemAlert.id)).where(
            SystemAlert.status == "active"
        )
        total = await db.scalar(total_stmt)

        # 严重告警数
        critical_stmt = sql_select(func.count(SystemAlert.id)).where(
            and_(
                SystemAlert.status == "active",
                SystemAlert.severity == "critical"
            )
        )
        critical = await db.scalar(critical_stmt)

        return {
            "total": total or 0,
            "critical": critical or 0
        }

    except Exception as e:
        logger.error(f"Failed to get active alerts count: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alert count")


# ============ SLA Management Endpoints ============


@router.get("/sla/report")
async def get_sla_report(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
    period_type: str = Query("daily", description="Period type (hourly/daily/weekly/monthly)"),
    limit: int = Query(30, ge=1, le=365, description="Number of records to return")
):
    """
    获取SLA报告

    返回指定周期类型的历史SLA记录
    """
    try:
        sla_service = SLAService(db)
        sla_records = await sla_service.get_sla_report(period_type, limit)

        # 转换为字典格式
        records = []
        for record in sla_records:
            records.append({
                "id": record.id,
                "period_start": record.period_start.isoformat(),
                "period_end": record.period_end.isoformat(),
                "period_type": record.period_type,
                "uptime_seconds": record.uptime_seconds,
                "downtime_seconds": record.downtime_seconds,
                "uptime_percentage": record.uptime_percentage,
                "total_requests": record.total_requests,
                "successful_requests": record.successful_requests,
                "failed_requests": record.failed_requests,
                "success_rate": record.success_rate,
                "avg_response_time_ms": record.avg_response_time_ms,
                "p50_response_time_ms": record.p50_response_time_ms,
                "p95_response_time_ms": record.p95_response_time_ms,
                "p99_response_time_ms": record.p99_response_time_ms,
                "max_response_time_ms": record.max_response_time_ms,
                "total_alerts": record.total_alerts,
                "critical_alerts": record.critical_alerts,
                "warning_alerts": record.warning_alerts,
                "avg_cpu_usage": record.avg_cpu_usage,
                "avg_memory_usage": record.avg_memory_usage,
                "avg_disk_usage": record.avg_disk_usage,
                "created_at": record.created_at.isoformat(),
            })

        return {
            "period_type": period_type,
            "count": len(records),
            "records": records
        }

    except Exception as e:
        logger.error(f"Failed to get SLA report: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve SLA report")


@router.get("/sla/summary")
async def get_sla_summary(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
    days: int = Query(30, ge=1, le=365, description="Number of days to summarize")
):
    """
    获取SLA汇总统计

    返回指定天数内的SLA汇总数据
    """
    try:
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=days)

        sla_service = SLAService(db)
        summary = await sla_service.get_sla_summary(period_start, period_end)

        return summary

    except Exception as e:
        logger.error(f"Failed to get SLA summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve SLA summary")


@router.post("/sla/generate")
async def generate_sla_report(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
    period_type: str = Query("hourly", description="Period type (hourly/daily)")
):
    """
    手动生成SLA报告

    立即生成指定周期的SLA报告
    """
    try:
        if period_type == "hourly":
            sla_record = await generate_hourly_sla(db)
        elif period_type == "daily":
            sla_record = await generate_daily_sla(db)
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid period type. Use 'hourly' or 'daily'"
            )

        if not sla_record:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate SLA report. No metrics data available."
            )

        return {
            "success": True,
            "message": f"{period_type.capitalize()} SLA report generated successfully",
            "sla": {
                "id": sla_record.id,
                "period_start": sla_record.period_start.isoformat(),
                "period_end": sla_record.period_end.isoformat(),
                "uptime_percentage": sla_record.uptime_percentage,
                "avg_response_time_ms": sla_record.avg_response_time_ms,
                "total_alerts": sla_record.total_alerts,
                "critical_alerts": sla_record.critical_alerts,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate SLA report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate SLA report")


@router.get("/sla/current")
async def get_current_sla(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """
    获取当前实时SLA状态

    计算并返回当天到目前为止的SLA指标
    """
    try:
        now = datetime.utcnow()
        # 今天凌晨
        period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_end = now

        sla_service = SLAService(db)

        # 临时计算当前SLA（不保存到数据库）
        from sqlalchemy import select, and_
        from app.models.system_metrics import SystemMetrics, SystemAlert
        import statistics

        # 查询今天的指标
        stmt = select(SystemMetrics).where(
            and_(
                SystemMetrics.timestamp >= period_start,
                SystemMetrics.timestamp < period_end
            )
        ).order_by(SystemMetrics.timestamp)

        result = await db.execute(stmt)
        metrics = list(result.scalars().all())

        if not metrics:
            return {
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "uptime_percentage": 100.0,
                "message": "No metrics data available for today"
            }

        # 简单计算
        unhealthy_count = sum(1 for m in metrics if m.overall_status == "unhealthy")
        uptime_percentage = ((len(metrics) - unhealthy_count) / len(metrics) * 100) if metrics else 100.0

        # 计算平均响应时间
        db_times = [m.db_response_time_ms for m in metrics if m.db_response_time_ms is not None]
        avg_db_response = statistics.mean(db_times) if db_times else None

        # 查询今天的告警
        alert_stmt = select(func.count(SystemAlert.id)).where(
            SystemAlert.triggered_at >= period_start
        )
        total_alerts = await db.scalar(alert_stmt)

        critical_stmt = select(func.count(SystemAlert.id)).where(
            and_(
                SystemAlert.triggered_at >= period_start,
                SystemAlert.severity == "critical"
            )
        )
        critical_alerts = await db.scalar(critical_stmt)

        return {
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "elapsed_hours": round((period_end - period_start).total_seconds() / 3600, 2),
            "uptime_percentage": round(uptime_percentage, 4),
            "metrics_collected": len(metrics),
            "avg_db_response_time_ms": round(avg_db_response, 2) if avg_db_response else None,
            "total_alerts": total_alerts or 0,
            "critical_alerts": critical_alerts or 0,
            "status": "healthy" if uptime_percentage >= 99.9 else "degraded" if uptime_percentage >= 99.0 else "poor"
        }

    except Exception as e:
        logger.error(f"Failed to get current SLA: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve current SLA")
