"""
Celery 应用配置
"""

from celery import Celery
from celery.schedules import crontab

from app.config import settings

# 创建 Celery 应用
celery_app = Celery(
    "videosite",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.scheduled_publish",  # 原有调度任务
        "app.tasks.scheduler_executor",  # 调度任务执行器
        "app.tasks.scheduler_optimizer",  # 调度任务优化器
        "app.tasks.scheduler_monitor",  # 调度任务监控器
        "app.tasks.transcode_av1",  # 转码任务（如果存在）
        "app.tasks.cleanup_temp_uploads",  # 🆕 临时文件清理任务
        "app.tasks.generate_sla_reports",  # 🆕 SLA报告生成任务
    ],
)

# Celery 配置
celery_app.conf.update(
    # 时区设置
    timezone="UTC",
    enable_utc=True,
    # 任务结果过期时间（秒）
    result_expires=3600,
    # 任务序列化
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # 任务追踪
    task_track_started=True,
    task_acks_late=True,
    # Worker 配置
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    # Beat 调度配置
    beat_schedule={
        # ========== 核心调度任务 ==========
        # 每分钟检查到期的调度任务（增强版）
        "execute-due-schedules-enhanced": {
            "task": "scheduler.execute_due_schedules",
            "schedule": crontab(minute="*"),  # 每分钟
            "options": {"queue": "scheduler", "expires": 50},
        },
        # 原有的调度检查（保留作为备份）
        "check-due-schedules": {
            "task": "scheduling.check_due_schedules",
            "schedule": 60.0,  # 每60秒
            "options": {"expires": 50},  # 任务50秒后过期
        },
        # 每小时检查过期的调度
        "check-expired-schedules": {
            "task": "scheduling.check_expired_schedules",
            "schedule": 3600.0,  # 每小时
            "options": {"expires": 3500},
        },
        # 每5分钟发送调度提醒
        "send-schedule-reminders": {
            "task": "scheduling.send_schedule_reminders",
            "schedule": 300.0,  # 每5分钟
            "options": {"expires": 290},
        },
        # 每天凌晨3点清理旧历史记录
        "cleanup-old-histories": {
            "task": "scheduling.cleanup_old_histories",
            "schedule": crontab(hour=3, minute=0),
        },
        # ========== 智能优化任务 ==========
        # 每6小时优化调度时间
        "optimize-schedule-times": {
            "task": "scheduler.optimize_schedule_times",
            "schedule": crontab(hour="*/6", minute=0),  # 每6小时
            "options": {"queue": "scheduler"},
        },
        # 每小时检测冲突
        "detect-conflicts": {
            "task": "scheduler.detect_conflicts",
            "schedule": crontab(hour="*", minute=30),  # 每小时30分
            "options": {"queue": "scheduler"},
        },
        # 每天凌晨2点生成报告
        "generate-daily-report": {
            "task": "scheduler.generate_daily_report",
            "schedule": crontab(hour=2, minute=0),
            "options": {"queue": "scheduler"},
        },
        # 每30分钟健康检查
        "health-check": {
            "task": "scheduler.health_check",
            "schedule": crontab(minute="*/30"),
            "options": {"queue": "scheduler"},
        },
        # ========== 上传文件清理任务 ==========
        # 每小时清理临时上传文件
        "cleanup-temp-uploads": {
            "task": "cleanup_temp_uploads",
            "schedule": crontab(hour="*", minute=15),  # 每小时15分
            "options": {"queue": "cleanup"},
        },
        # 每6小时清理过期的Redis会话
        "cleanup-expired-redis-sessions": {
            "task": "cleanup_expired_redis_sessions",
            "schedule": crontab(hour="*/6", minute=30),  # 每6小时
            "options": {"queue": "cleanup"},
        },
        # 每天凌晨4点检查孤立的multipart uploads
        "cleanup-orphaned-multipart-uploads": {
            "task": "cleanup_orphaned_multipart_uploads",
            "schedule": crontab(hour=4, minute=0),
            "options": {"queue": "cleanup"},
        },
        # ========== SLA报告生成任务 ==========
        # 每小时第5分钟生成小时SLA报告
        "generate-hourly-sla": {
            "task": "generate_hourly_sla_report",
            "schedule": crontab(minute=5),  # 每小时的第5分钟
            "options": {"queue": "monitoring"},
        },
        # 每天凌晨00:10生成日报
        "generate-daily-sla": {
            "task": "generate_daily_sla_report",
            "schedule": crontab(hour=0, minute=10),  # 每天00:10
            "options": {"queue": "monitoring"},
        },
        # 每周一凌晨00:30生成周报
        "generate-weekly-sla": {
            "task": "generate_weekly_sla_report",
            "schedule": crontab(day_of_week=1, hour=0, minute=30),  # 每周一00:30
            "options": {"queue": "monitoring"},
        },
        # 每月1号凌晨01:00生成月报
        "generate-monthly-sla": {
            "task": "generate_monthly_sla_report",
            "schedule": crontab(day_of_month=1, hour=1, minute=0),  # 每月1号01:00
            "options": {"queue": "monitoring"},
        },
    },
)

# 自动发现任务
celery_app.autodiscover_tasks(["app.tasks"])


if __name__ == "__main__":
    celery_app.start()
