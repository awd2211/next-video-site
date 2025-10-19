"""
性能分析工具
自动分析函数执行时间、内存使用、SQL查询等
"""

import asyncio
import functools
import time
from contextlib import asynccontextmanager
from typing import Any, Callable

from loguru import logger


class PerformanceProfiler:
    """性能分析器"""

    # 存储性能统计数据
    stats = {}

    @classmethod
    def profile(cls, func_name: str | None = None):
        """
        性能分析装饰器

        Args:
            func_name: 函数名称（可选，默认使用函数的__name__）

        Example:
            @PerformanceProfiler.profile()
            async def expensive_operation():
                # 自动记录执行时间、调用次数
                ...

            # 查看统计
            stats = PerformanceProfiler.get_stats()
        """

        def decorator(func: Callable) -> Callable:
            name = func_name or func.__name__

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                # 初始化统计
                if name not in cls.stats:
                    cls.stats[name] = {
                        "count": 0,
                        "total_time": 0.0,
                        "min_time": float("inf"),
                        "max_time": 0.0,
                        "errors": 0,
                    }

                start_time = time.time()
                start_memory = None

                # 尝试获取内存使用（可选）
                try:
                    import psutil

                    process = psutil.Process()
                    start_memory = process.memory_info().rss / 1024 / 1024  # MB
                except ImportError:
                    pass

                try:
                    # 执行函数
                    result = await func(*args, **kwargs)

                    # 记录成功执行
                    duration = time.time() - start_time
                    cls.stats[name]["count"] += 1
                    cls.stats[name]["total_time"] += duration
                    cls.stats[name]["min_time"] = min(
                        cls.stats[name]["min_time"], duration
                    )
                    cls.stats[name]["max_time"] = max(
                        cls.stats[name]["max_time"], duration
                    )

                    # 记录内存增量（如果可用）
                    if start_memory:
                        end_memory = (
                            psutil.Process().memory_info().rss / 1024 / 1024
                        )
                        memory_delta = end_memory - start_memory
                        cls.stats[name]["memory_delta"] = cls.stats[name].get(
                            "memory_delta", 0
                        ) + memory_delta

                    # 警告慢函数
                    if duration > 1.0:
                        logger.warning(
                            f"⚠️ Slow function: {name} took {duration:.3f}s"
                        )

                    return result

                except Exception as e:
                    cls.stats[name]["errors"] += 1
                    raise

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                # 同步函数版本
                if name not in cls.stats:
                    cls.stats[name] = {
                        "count": 0,
                        "total_time": 0.0,
                        "min_time": float("inf"),
                        "max_time": 0.0,
                        "errors": 0,
                    }

                start_time = time.time()

                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time

                    cls.stats[name]["count"] += 1
                    cls.stats[name]["total_time"] += duration
                    cls.stats[name]["min_time"] = min(
                        cls.stats[name]["min_time"], duration
                    )
                    cls.stats[name]["max_time"] = max(
                        cls.stats[name]["max_time"], duration
                    )

                    return result

                except Exception:
                    cls.stats[name]["errors"] += 1
                    raise

            # 返回适当的wrapper
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

        return decorator

    @classmethod
    def get_stats(cls, sort_by: str = "total_time") -> list[dict]:
        """
        获取性能统计数据

        Args:
            sort_by: 排序字段（total_time, count, avg_time）

        Returns:
            统计数据列表
        """
        result = []

        for name, stats in cls.stats.items():
            avg_time = (
                stats["total_time"] / stats["count"] if stats["count"] > 0 else 0
            )

            result.append(
                {
                    "function": name,
                    "calls": stats["count"],
                    "total_time": round(stats["total_time"], 3),
                    "avg_time": round(avg_time, 3),
                    "min_time": round(stats["min_time"], 3)
                    if stats["min_time"] != float("inf")
                    else 0,
                    "max_time": round(stats["max_time"], 3),
                    "errors": stats["errors"],
                    "memory_delta_mb": round(stats.get("memory_delta", 0), 2),
                }
            )

        # 排序
        if sort_by == "total_time":
            result.sort(key=lambda x: x["total_time"], reverse=True)
        elif sort_by == "count":
            result.sort(key=lambda x: x["calls"], reverse=True)
        elif sort_by == "avg_time":
            result.sort(key=lambda x: x["avg_time"], reverse=True)

        return result

    @classmethod
    def reset_stats(cls):
        """重置所有统计数据"""
        cls.stats = {}

    @classmethod
    def print_stats(cls, top_n: int = 10):
        """
        打印性能统计（控制台输出）

        Args:
            top_n: 显示前N个最慢的函数
        """
        stats = cls.get_stats(sort_by="total_time")[:top_n]

        if not stats:
            logger.info("No performance statistics available")
            return

        logger.info("\n" + "=" * 80)
        logger.info(f"📊 Performance Statistics (Top {top_n})")
        logger.info("=" * 80)
        logger.info(
            f"{'Function':<40} {'Calls':>8} {'Total':>10} {'Avg':>10} {'Max':>10}"
        )
        logger.info("-" * 80)

        for stat in stats:
            logger.info(
                f"{stat['function']:<40} "
                f"{stat['calls']:>8} "
                f"{stat['total_time']:>9.3f}s "
                f"{stat['avg_time']:>9.3f}s "
                f"{stat['max_time']:>9.3f}s"
            )

        logger.info("=" * 80 + "\n")


@asynccontextmanager
async def profile_block(name: str):
    """
    性能分析上下文管理器（用于代码块）

    Example:
        async with profile_block("complex_calculation"):
            # 被分析的代码块
            result = await complex_calculation()
    """
    start_time = time.time()

    try:
        yield
    finally:
        duration = time.time() - start_time
        logger.info(f"⏱️ Block '{name}' took {duration:.3f}s")


class QueryProfiler:
    """SQL查询性能分析器"""

    queries = []
    enabled = False

    @classmethod
    def enable(cls):
        """启用查询分析"""
        cls.enabled = True
        cls.queries = []

    @classmethod
    def disable(cls):
        """禁用查询分析"""
        cls.enabled = False

    @classmethod
    def record_query(cls, sql: str, duration: float, params: dict | None = None):
        """
        记录SQL查询

        Args:
            sql: SQL语句
            duration: 执行时间
            params: 查询参数
        """
        if not cls.enabled:
            return

        cls.queries.append(
            {
                "sql": sql,
                "duration": duration,
                "params": params,
                "timestamp": time.time(),
            }
        )

    @classmethod
    def get_slow_queries(cls, threshold: float = 0.1) -> list[dict]:
        """
        获取慢查询

        Args:
            threshold: 慢查询阈值（秒）

        Returns:
            慢查询列表
        """
        return [q for q in cls.queries if q["duration"] > threshold]

    @classmethod
    def detect_n_plus_one(cls) -> list[dict]:
        """
        检测N+1查询问题

        Returns:
            可疑的N+1查询模式
        """
        # 简单检测：相似的查询多次执行
        from collections import Counter

        # 提取查询模式（去除具体参数）
        patterns = []
        for q in cls.queries:
            # 简化SQL（去除WHERE条件中的具体值）
            simplified = q["sql"].split("WHERE")[0].strip()
            patterns.append(simplified)

        # 统计重复查询
        pattern_counts = Counter(patterns)

        # 找出执行次数 > 5 的模式
        suspicious = []
        for pattern, count in pattern_counts.items():
            if count > 5:
                suspicious.append(
                    {
                        "pattern": pattern,
                        "count": count,
                        "warning": "Possible N+1 query detected",
                    }
                )

        return suspicious

    @classmethod
    def get_summary(cls) -> dict:
        """获取查询统计摘要"""
        if not cls.queries:
            return {"total_queries": 0}

        total_time = sum(q["duration"] for q in cls.queries)
        avg_time = total_time / len(cls.queries)

        return {
            "total_queries": len(cls.queries),
            "total_time": round(total_time, 3),
            "avg_time": round(avg_time, 3),
            "slow_queries": len(cls.get_slow_queries(0.1)),
            "n_plus_one_suspects": len(cls.detect_n_plus_one()),
        }

    @classmethod
    def reset(cls):
        """重置查询记录"""
        cls.queries = []
