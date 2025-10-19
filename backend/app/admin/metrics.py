"""
管理员 - 性能指标端点
"""

from fastapi import APIRouter, Depends, Query

from app.models.user import AdminUser
from app.utils.dependencies import get_current_admin_user
from app.utils.metrics import Metrics, collect_system_metrics
from app.utils.profiler import PerformanceProfiler, QueryProfiler

router = APIRouter()


@router.get("/metrics")
async def get_metrics(
    metric_name: str | None = None,
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取应用性能指标

    Args:
        metric_name: 可选的指标名称过滤

    Returns:
        指标数据
    """
    # 先收集最新的系统指标
    await collect_system_metrics()

    # 获取指标
    metrics = await Metrics.get_metrics(metric_name)

    return {
        "metrics": metrics,
        "total": len(metrics),
        "timestamp": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
    }


@router.get("/metrics/summary")
async def get_metrics_summary(
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取指标摘要（仪表板用）

    Returns:
        关键指标摘要
    """
    await collect_system_metrics()
    all_metrics = await Metrics.get_metrics()

    # 提取关键指标
    summary = {
        "database": {
            "pool_size": all_metrics.get("gauge:db_pool_size", "N/A"),
            "checked_out": all_metrics.get("gauge:db_pool_checked_out", "N/A"),
            "checked_in": all_metrics.get("gauge:db_pool_checked_in", "N/A"),
            "overflow": all_metrics.get("gauge:db_pool_overflow", "N/A"),
        },
        "cache": {
            "hit_rate": all_metrics.get("gauge:cache_hit_rate", "N/A"),
            "total_requests": all_metrics.get("gauge:cache_total_requests", "N/A"),
        },
        "api": {
            # 计算API请求总数
            "total_requests": sum(
                int(v)
                for k, v in all_metrics.items()
                if k.startswith("api_requests_total:")
            ),
        },
        "videos": {
            "total_views": all_metrics.get("video_views_total", "0"),
        },
    }

    return summary


@router.delete("/metrics")
async def clear_metrics(
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    清除所有指标（仅用于测试/重置）

    需要管理员权限
    """
    await Metrics.clear_metrics()
    return {"message": "All metrics cleared successfully"}


@router.get("/profiler/functions")
async def get_function_performance(
    sort_by: str = Query("total_time", regex="^(total_time|count|avg_time)$"),
    top_n: int = Query(20, ge=1, le=100),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取函数性能分析数据

    Args:
        sort_by: 排序字段
        top_n: 返回前N个函数

    Returns:
        函数性能统计
    """
    stats = PerformanceProfiler.get_stats(sort_by=sort_by)[:top_n]

    return {
        "total_functions": len(PerformanceProfiler.stats),
        "displayed": len(stats),
        "functions": stats,
    }


@router.delete("/profiler/functions")
async def reset_function_profiler(
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """重置函数性能统计"""
    PerformanceProfiler.reset_stats()
    return {"message": "Function profiler statistics reset successfully"}


@router.get("/profiler/queries")
async def get_query_performance(
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取SQL查询性能分析

    Returns:
        查询性能统计和N+1检测结果
    """
    summary = QueryProfiler.get_summary()
    slow_queries = QueryProfiler.get_slow_queries(threshold=0.1)
    n_plus_one = QueryProfiler.detect_n_plus_one()

    return {
        "summary": summary,
        "slow_queries": slow_queries[:20],  # 前20个慢查询
        "n_plus_one_suspects": n_plus_one,
    }


@router.post("/profiler/queries/enable")
async def enable_query_profiler(
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    启用SQL查询分析

    注意：会记录所有SQL查询，对性能有轻微影响
    """
    QueryProfiler.enable()
    return {
        "message": "Query profiler enabled",
        "warning": "This will record all SQL queries. Disable after debugging.",
    }


@router.post("/profiler/queries/disable")
async def disable_query_profiler(
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """禁用SQL查询分析"""
    QueryProfiler.disable()
    return {"message": "Query profiler disabled"}


@router.delete("/profiler/queries")
async def reset_query_profiler(
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """重置查询性能统计"""
    QueryProfiler.reset()
    return {"message": "Query profiler statistics reset successfully"}
