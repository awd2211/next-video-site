"""
Celery任务监控工具
监控任务队列状态、失败任务等
"""

import logging
from datetime import datetime
from typing import Dict

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
            from app.celery_app import celery_app

            # 获取队列信息
            inspect = celery_app.control.inspect()

            # 获取活跃任务
            active_tasks = inspect.active()

            # 获取保留任务
            reserved_tasks = inspect.reserved()

            # 获取已注册任务
            registered_tasks = inspect.registered()

            # 获取调度任务（scheduled）
            scheduled_tasks = inspect.scheduled()

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
            total_scheduled = (
                sum(len(tasks) for tasks in scheduled_tasks.values())
                if scheduled_tasks
                else 0
            )

            # 提取活跃任务列表（最多10个）
            active_task_list = []
            if active_tasks:
                for worker_name, tasks in active_tasks.items():
                    for task in tasks[:5]:  # 每个worker最多5个
                        active_task_list.append({
                            "task_id": task.get("id", "unknown"),
                            "task_name": task.get("name", "unknown"),
                            "worker": worker_name,
                            "args": str(task.get("args", []))[:50],  # 限制长度
                            "kwargs": str(task.get("kwargs", {}))[:50],
                        })

            # 提取预留任务列表（最多10个）
            reserved_task_list = []
            if reserved_tasks:
                for worker_name, tasks in reserved_tasks.items():
                    for task in tasks[:5]:
                        reserved_task_list.append({
                            "task_id": task.get("id", "unknown"),
                            "task_name": task.get("name", "unknown"),
                            "worker": worker_name,
                        })

            return {
                "status": "ok",
                "active_tasks": total_active,
                "reserved_tasks": total_reserved,
                "scheduled_tasks": total_scheduled,
                "workers_count": (len(active_tasks) if active_tasks else 0),
                "registered_tasks": (
                    list(registered_tasks.values())[0] if registered_tasks else []
                ),
                "active_task_list": active_task_list,
                "reserved_task_list": reserved_task_list,
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
            from app.celery_app import celery_app

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
                        "total_tasks": worker_stats.get("total", {}),
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
    def get_task_stats() -> Dict:
        """
        获取任务执行统计（成功/失败）

        Returns:
            任务统计字典
        """
        try:
            from app.celery_app import celery_app

            inspect = celery_app.control.inspect()
            stats = inspect.stats()

            if not stats:
                return {
                    "status": "warning",
                    "total_succeeded": 0,
                    "total_failed": 0,
                    "message": "No worker stats available",
                }

            total_succeeded = 0
            total_failed = 0

            for worker_name, worker_stats in stats.items():
                # 从worker统计中获取成功和失败的任务数
                total_dict = worker_stats.get("total", {})
                total_succeeded += sum(
                    count for task, count in total_dict.items()
                    if isinstance(count, int)
                )

            return {
                "status": "ok",
                "total_succeeded": total_succeeded,
                "total_failed": total_failed,
                "message": "Task statistics retrieved",
            }
        except Exception as e:
            logger.error(f"获取任务统计失败: {e}")
            return {
                "status": "error",
                "total_succeeded": 0,
                "total_failed": 0,
                "message": str(e),
            }

    @staticmethod
    def check_health() -> Dict:
        """
        健康检查

        Returns:
            健康状态字典
        """
        try:
            from app.celery_app import celery_app

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
