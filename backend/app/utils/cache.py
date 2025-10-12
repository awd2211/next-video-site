"""
Redis缓存工具类
提供通用的缓存操作，用于缓存频繁访问的数据

注意：使用JSON序列化而非pickle，避免远程代码执行风险
"""

import json
from datetime import datetime
from decimal import Decimal
from functools import wraps
from typing import Any, Callable

import redis.asyncio as redis
from loguru import logger

from app.config import settings


def json_serializer(obj: Any) -> str:
    """
    JSON序列化器，支持datetime等特殊类型

    Args:
        obj: 要序列化的对象

    Returns:
        JSON字符串
    """

    def default(o):
        if isinstance(o, datetime):
            return {"__type__": "datetime", "value": o.isoformat()}
        elif isinstance(o, Decimal):
            return {"__type__": "decimal", "value": str(o)}
        elif hasattr(o, "model_dump"):
            # Pydantic v2 models
            return o.model_dump(mode="json")
        elif hasattr(o, "dict"):
            # Pydantic v1 models (legacy)
            return o.dict()
        elif hasattr(o, "__dict__"):
            # Other objects with __dict__
            return vars(o)
        return str(o)

    return json.dumps(obj, default=default, ensure_ascii=False)


def json_deserializer(json_str: str) -> Any:
    """
    JSON反序列化器，恢复datetime等特殊类型

    Args:
        json_str: JSON字符串

    Returns:
        反序列化的对象
    """

    def object_hook(obj):
        if isinstance(obj, dict) and "__type__" in obj:
            if obj["__type__"] == "datetime":
                return datetime.fromisoformat(obj["value"])
            elif obj["__type__"] == "decimal":
                return Decimal(obj["value"])
        return obj

    return json.loads(json_str, object_hook=object_hook)


# 创建Redis连接池
redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,  # 使用字符串模式（JSON）
    max_connections=50,
)


async def get_redis() -> redis.Redis:
    """获取Redis客户端"""
    return redis.Redis(connection_pool=redis_pool)


class CacheStats:
    """缓存统计类"""

    @staticmethod
    async def record_hit():
        """记录缓存命中"""
        try:
            client = await get_redis()
            today = datetime.now().strftime("%Y-%m-%d")
            await client.incr(f"cache_stats:hits:{today}")
            await client.expire(f"cache_stats:hits:{today}", 86400 * 7)  # 保留7天
        except Exception as e:
            logger.error(f"Cache stats record hit error: {e}", exc_info=True)

    @staticmethod
    async def record_miss():
        """记录缓存未命中"""
        try:
            client = await get_redis()
            today = datetime.now().strftime("%Y-%m-%d")
            await client.incr(f"cache_stats:misses:{today}")
            await client.expire(f"cache_stats:misses:{today}", 86400 * 7)  # 保留7天
        except Exception as e:
            logger.error(f"Cache stats record miss error: {e}", exc_info=True)

    @staticmethod
    async def get_stats(days: int = 7) -> dict:
        """获取缓存统计信息"""
        try:
            client = await get_redis()
            stats = []

            for i in range(days):
                date = datetime.now()
                if i > 0:
                    from datetime import timedelta

                    date = date - timedelta(days=i)

                date_str = date.strftime("%Y-%m-%d")

                hits = await client.get(f"cache_stats:hits:{date_str}")
                misses = await client.get(f"cache_stats:misses:{date_str}")

                hits = int(hits) if hits else 0
                misses = int(misses) if misses else 0
                total = hits + misses
                hit_rate = (hits / total * 100) if total > 0 else 0

                stats.append(
                    {
                        "date": date_str,
                        "hits": hits,
                        "misses": misses,
                        "total": total,
                        "hit_rate": round(hit_rate, 2),
                    }
                )

            return {
                "stats": stats[::-1],  # 倒序，最新的在前
                "summary": {
                    "total_hits": sum(s["hits"] for s in stats),
                    "total_misses": sum(s["misses"] for s in stats),
                    "total_requests": sum(s["total"] for s in stats),
                    "average_hit_rate": round(
                        (
                            sum(s["hits"] for s in stats)
                            / sum(s["total"] for s in stats)
                            * 100
                            if sum(s["total"] for s in stats) > 0
                            else 0
                        ),
                        2,
                    ),
                },
            }
        except Exception as e:
            logger.error(f"Cache stats get error: {e}", exc_info=True)
            return {"stats": [], "summary": {}}


class Cache:
    """缓存管理类"""

    @staticmethod
    async def get(key: str, default: Any = None) -> Any:
        """
        从缓存获取数据

        Args:
            key: 缓存键
            default: 默认值

        Returns:
            缓存的数据或默认值
        """
        try:
            client = await get_redis()
            value = await client.get(key)
            if value is None:
                # 记录缓存未命中
                await CacheStats.record_miss()
                return default
            # 记录缓存命中
            await CacheStats.record_hit()
            # 使用JSON反序列化
            return json_deserializer(value)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}", exc_info=True)
            return default

    @staticmethod
    async def set(key: str, value: Any, ttl: int = 3600) -> bool:
        """
        设置缓存

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），默认1小时

        Returns:
            是否成功
        """
        try:
            client = await get_redis()
            # 使用JSON序列化，安全且高效
            serialized = json_serializer(value)
            await client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}", exc_info=True)
            return False

    @staticmethod
    async def delete(key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            是否成功
        """
        try:
            client = await get_redis()
            await client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}", exc_info=True)
            return False

    @staticmethod
    async def delete_pattern(pattern: str) -> int:
        """
        删除匹配模式的所有缓存

        Args:
            pattern: 键模式，如 "categories:*"

        Returns:
            删除的键数量
        """
        try:
            client = await get_redis()
            keys = []
            async for key in client.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                return await client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}", exc_info=True)
            return 0

    @staticmethod
    async def exists(key: str) -> bool:
        """
        检查缓存是否存在

        Args:
            key: 缓存键

        Returns:
            是否存在
        """
        try:
            client = await get_redis()
            return await client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}", exc_info=True)
            return False


def cache_result(key_prefix: str, ttl: int = 3600):
    """
    装饰器：缓存函数结果

    Args:
        key_prefix: 缓存键前缀
        ttl: 过期时间（秒）

    Example:
        @cache_result("categories:all", ttl=1800)
        async def get_all_categories():
            # 数据库查询
            return categories
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键（包含函数参数）
            cache_key = f"{key_prefix}"
            if args or kwargs:
                # 将参数序列化为字符串作为键的一部分
                args_str = json.dumps(
                    {"args": args, "kwargs": kwargs}, sort_keys=True, default=str
                )
                cache_key = f"{key_prefix}:{hash(args_str)}"

            # 尝试从缓存获取
            cached = await Cache.get(cache_key)
            if cached is not None:
                return cached

            # 执行函数获取结果
            result = await func(*args, **kwargs)

            # 缓存结果
            if result is not None:
                await Cache.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


async def clear_cache_by_prefix(prefix: str):
    """
    清除指定前缀的所有缓存

    Args:
        prefix: 缓存键前缀
    """
    await Cache.delete_pattern(f"{prefix}:*")
