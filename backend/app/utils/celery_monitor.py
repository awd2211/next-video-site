"""
Celery任务监控工具
监控任务队列状态、失败任务等
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CeleryMonitor:
    """Celery任务监控器"""

    @staticmethod
    def get_queue_stats() -> Dict:
        """
        获取队列统计信息
        
        Returns:
            队列状态字典
        """
        try:
            from app.tasks.transcode_av1 import celery_app
            
            # 获取队列信息
            inspect = celery_app.control.inspect()
            
            # 获取活跃任务
            active_tasks = inspect.active()
            
            # 获取保留任务
            reserved_tasks = inspect.reserved()
            
            # 获取已注册任务
            registered_tasks = inspect.registered()
            
            # 统计
            total_active = (
                sum(len(tasks) for tasks in active_tasks.values())
                if active_tasks
                else 0
            )
            total_reserved = (
                sum(len(tasks) for tasks in reserved_tasks.values())
                if reserved_tasks
                else 0
            )
            
            return {
                "status": "ok",
                "active_tasks": total_active,
                "reserved_tasks": total_reserved,
                "workers_count": (
                    len(active_tasks) if active_tasks else 0
                ),
                "registered_tasks": (
                    list(registered_tasks.values())[0]
                    if registered_tasks
                    else []
                ),
                "timestamp": datetime.now().isoformat(),
            }
        except ImportError:
            return {
                "status": "error",
                "message": "Celery未配置或未启动",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取Celery队列状态失败: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    @staticmethod
    def get_worker_stats() -> Dict:
        """
        获取Worker统计信息
        
        Returns:
            Worker状态字典
        """
        try:
            from app.tasks.transcode_av1 import celery_app
            
            inspect = celery_app.control.inspect()
            
            # 获取Worker统计信息
            stats = inspect.stats()
            
            if not stats:
                return {
                    "status": "warning",
                    "message": "没有活跃的Worker",
                    "workers": [],
                }
            
            workers = []
            for worker_name, worker_stats in stats.items():
                workers.append(
                    {
                        "name": worker_name,
                        "pool": worker_stats.get("pool", {}),
                        "total_tasks": worker_stats.get(
                            "total", {}
                        ),
                    }
                )
            
            return {
                "status": "ok",
                "workers_count": len(workers),
                "workers": workers,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取Worker统计信息失败: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    @staticmethod
    def check_health() -> Dict:
        """
        健康检查
        
        Returns:
            健康状态字典
        """
        try:
            from app.tasks.transcode_av1 import celery_app
            
            # Ping所有Worker
            inspect = celery_app.control.inspect()
            ping_result = inspect.ping()
            
            if not ping_result:
                return {
                    "healthy": False,
                    "message": "没有Worker响应",
                    "timestamp": datetime.now().isoformat(),
                }
            
            return {
                "healthy": True,
                "workers_responding": len(ping_result),
                "worker_names": list(ping_result.keys()),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Celery健康检查失败: {e}")
            return {
                "healthy": False,
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
            }

