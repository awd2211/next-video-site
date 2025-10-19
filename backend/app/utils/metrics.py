"""
性能指标收集器
提供简单的metrics API，可轻松集成到Prometheus

使用Redis存储指标，避免内存泄漏
"""

import time
from datetime import datetime
from typing import Optional

from loguru import logger

from app.utils.cache import get_redis


class Metrics:
    """应用性能指标收集器"""

    # Metrics 键前缀
    PREFIX = "metrics"

    @staticmethod
    async def increment(metric_name: str, value: int = 1, labels: Optional[dict] = None):
        """
        增量计数器

        Args:
            metric_name: 指标名称 (e.g., "api_requests_total")
            value: 增量值
            labels: 标签字典 (e.g., {"method": "GET", "path": "/api/v1/videos"})
        """
        try:
            redis_client = await get_redis()

            # 构建键名
            key = f"{Metrics.PREFIX}:{metric_name}"
            if labels:
                label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
                key = f"{key}:{label_str}"

            await redis_client.incrby(key, value)

            # 设置过期时间（保留7天数据）
            await redis_client.expire(key, 7 * 86400)

        except Exception as e:
            logger.error(f"Failed to increment metric {metric_name}: {e}")

    @staticmethod
    async def gauge(metric_name: str, value: float, labels: Optional[dict] = None):
        """
        设置仪表盘值（当前状态值）

        Args:
            metric_name: 指标名称 (e.g., "database_pool_connections")
            value: 当前值
            labels: 标签字典
        """
        try:
            redis_client = await get_redis()

            key = f"{Metrics.PREFIX}:gauge:{metric_name}"
            if labels:
                label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
                key = f"{key}:{label_str}"

            await redis_client.set(key, str(value), ex=7 * 86400)

        except Exception as e:
            logger.error(f"Failed to set gauge {metric_name}: {e}")

    @staticmethod
    async def histogram(
        metric_name: str, value: float, labels: Optional[dict] = None
    ):
        """
        记录直方图值（用于延迟、大小等分布式数据）

        Args:
            metric_name: 指标名称 (e.g., "api_request_duration_seconds")
            value: 测量值
            labels: 标签字典
        """
        try:
            redis_client = await get_redis()

            # 存储到有序集合，便于计算分位数
            key = f"{Metrics.PREFIX}:histogram:{metric_name}"
            if labels:
                label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
                key = f"{key}:{label_str}"

            # 使用时间戳作为score，值作为member
            await redis_client.zadd(key, {str(value): time.time()})

            # 限制集合大小（保留最近10000个值）
            await redis_client.zremrangebyrank(key, 0, -10001)

            # 设置过期时间
            await redis_client.expire(key, 7 * 86400)

        except Exception as e:
            logger.error(f"Failed to record histogram {metric_name}: {e}")

    @staticmethod
    async def get_metrics(metric_name: Optional[str] = None) -> dict:
        """
        获取所有指标或特定指标

        Args:
            metric_name: 可选的指标名称过滤

        Returns:
            指标字典
        """
        try:
            redis_client = await get_redis()

            # 构建模式
            pattern = f"{Metrics.PREFIX}:*"
            if metric_name:
                pattern = f"{Metrics.PREFIX}:*{metric_name}*"

            metrics = {}
            async for key in redis_client.scan_iter(match=pattern):
                value = await redis_client.get(key)
                if value:
                    # 解析键名
                    clean_key = key.replace(f"{Metrics.PREFIX}:", "")
                    metrics[clean_key] = value

            return metrics

        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {}

    @staticmethod
    async def clear_metrics():
        """清除所有指标（用于测试）"""
        try:
            redis_client = await get_redis()
            async for key in redis_client.scan_iter(match=f"{Metrics.PREFIX}:*"):
                await redis_client.delete(key)
        except Exception as e:
            logger.error(f"Failed to clear metrics: {e}")


class MetricsCollector:
    """指标收集器装饰器和上下文管理器"""

    @staticmethod
    def track_api_request(endpoint: str, method: str):
        """
        跟踪API请求的装饰器

        Usage:
            @MetricsCollector.track_api_request("/api/v1/videos", "GET")
            async def list_videos(...):
                ...
        """

        def decorator(func):
            async def wrapper(*args, **kwargs):
                start_time = time.time()

                try:
                    # 执行函数
                    result = await func(*args, **kwargs)

                    # 记录成功请求
                    await Metrics.increment(
                        "api_requests_total",
                        labels={"endpoint": endpoint, "method": method, "status": "success"},
                    )

                    # 记录响应时间
                    duration = time.time() - start_time
                    await Metrics.histogram(
                        "api_request_duration_seconds",
                        duration,
                        labels={"endpoint": endpoint, "method": method},
                    )

                    return result

                except Exception as e:
                    # 记录失败请求
                    await Metrics.increment(
                        "api_requests_total",
                        labels={
                            "endpoint": endpoint,
                            "method": method,
                            "status": "error",
                            "error_type": type(e).__name__,
                        },
                    )
                    raise

            return wrapper

        return decorator


# 便捷函数
async def track_cache_hit():
    """记录缓存命中"""
    await Metrics.increment("cache_hits_total")


async def track_cache_miss():
    """记录缓存未命中"""
    await Metrics.increment("cache_misses_total")


async def track_db_query(duration: float, operation: str = "select"):
    """记录数据库查询"""
    await Metrics.increment("db_queries_total", labels={"operation": operation})
    await Metrics.histogram(
        "db_query_duration_seconds", duration, labels={"operation": operation}
    )


async def track_video_view(video_id: int):
    """记录视频播放"""
    await Metrics.increment("video_views_total")
    await Metrics.increment(f"video_views_by_id", labels={"video_id": str(video_id)})


# 系统指标收集
async def collect_system_metrics():
    """收集系统级指标（连接池、缓存等）"""
    try:
        from app.database import get_pool_status

        # 数据库连接池
        pool_status = get_pool_status()
        await Metrics.gauge("db_pool_size", pool_status["pool_size"])
        await Metrics.gauge("db_pool_checked_out", pool_status["checked_out"])
        await Metrics.gauge("db_pool_checked_in", pool_status["checked_in"])
        await Metrics.gauge("db_pool_overflow", pool_status["overflow"])

        # Redis 缓存统计
        from app.utils.cache import CacheStats

        cache_stats = await CacheStats.get_stats(days=1)
        if cache_stats.get("summary"):
            summary = cache_stats["summary"]
            await Metrics.gauge("cache_hit_rate", summary.get("average_hit_rate", 0))
            await Metrics.gauge("cache_total_requests", summary.get("total_requests", 0))

    except Exception as e:
        logger.error(f"Failed to collect system metrics: {e}")
