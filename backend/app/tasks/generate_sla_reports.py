"""
定时生成SLA报告的Celery任务

按计划自动生成小时、每日、每周、每月的SLA报告
"""

from datetime import datetime
from loguru import logger

from app.celery_app import celery_app
from app.database import SessionLocal
from app.services.sla_service import (
    generate_hourly_sla,
    generate_daily_sla,
    generate_weekly_sla,
    generate_monthly_sla
)


@celery_app.task(name="generate_hourly_sla_report")
def generate_hourly_sla_report():
    """
    每小时生成一次SLA报告

    建议在每小时的第5分钟执行，例如: 00:05, 01:05, 02:05...
    这样可以确保上一个小时的所有指标都已收集完毕
    """
    db = SessionLocal()
    try:
        logger.info("Starting hourly SLA report generation")

        # 使用同步方式调用异步函数
        import asyncio
        loop = asyncio.get_event_loop()
        sla_record = loop.run_until_complete(generate_hourly_sla(db))

        if sla_record:
            logger.info(
                f"Hourly SLA report generated successfully: "
                f"{sla_record.period_start} to {sla_record.period_end}, "
                f"uptime: {sla_record.uptime_percentage}%"
            )
            return {
                "success": True,
                "sla_id": sla_record.id,
                "uptime_percentage": sla_record.uptime_percentage
            }
        else:
            logger.warning("Hourly SLA report generation returned None")
            return {
                "success": False,
                "message": "No metrics data available"
            }

    except Exception as e:
        logger.error(f"Failed to generate hourly SLA report: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="generate_daily_sla_report")
def generate_daily_sla_report():
    """
    每天生成一次SLA报告

    建议在每天凌晨00:10执行，确保前一天的所有数据都已收集
    """
    db = SessionLocal()
    try:
        logger.info("Starting daily SLA report generation")

        import asyncio
        loop = asyncio.get_event_loop()
        sla_record = loop.run_until_complete(generate_daily_sla(db))

        if sla_record:
            logger.info(
                f"Daily SLA report generated successfully: "
                f"{sla_record.period_start.date()} to {sla_record.period_end.date()}, "
                f"uptime: {sla_record.uptime_percentage}%, "
                f"alerts: {sla_record.total_alerts} (critical: {sla_record.critical_alerts})"
            )
            return {
                "success": True,
                "sla_id": sla_record.id,
                "uptime_percentage": sla_record.uptime_percentage,
                "total_alerts": sla_record.total_alerts
            }
        else:
            logger.warning("Daily SLA report generation returned None")
            return {
                "success": False,
                "message": "No metrics data available"
            }

    except Exception as e:
        logger.error(f"Failed to generate daily SLA report: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="generate_weekly_sla_report")
def generate_weekly_sla_report():
    """
    每周生成一次SLA报告

    建议在每周一凌晨00:30执行
    """
    db = SessionLocal()
    try:
        logger.info("Starting weekly SLA report generation")

        import asyncio
        loop = asyncio.get_event_loop()
        sla_record = loop.run_until_complete(generate_weekly_sla(db))

        if sla_record:
            logger.info(
                f"Weekly SLA report generated successfully: "
                f"{sla_record.period_start.date()} to {sla_record.period_end.date()}, "
                f"uptime: {sla_record.uptime_percentage}%"
            )
            return {
                "success": True,
                "sla_id": sla_record.id,
                "uptime_percentage": sla_record.uptime_percentage
            }
        else:
            logger.warning("Weekly SLA report generation returned None")
            return {
                "success": False,
                "message": "No metrics data available"
            }

    except Exception as e:
        logger.error(f"Failed to generate weekly SLA report: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="generate_monthly_sla_report")
def generate_monthly_sla_report():
    """
    每月生成一次SLA报告

    建议在每月1号凌晨01:00执行
    """
    db = SessionLocal()
    try:
        logger.info("Starting monthly SLA report generation")

        import asyncio
        loop = asyncio.get_event_loop()
        sla_record = loop.run_until_complete(generate_monthly_sla(db))

        if sla_record:
            logger.info(
                f"Monthly SLA report generated successfully: "
                f"{sla_record.period_start.strftime('%Y-%m')} "
                f"uptime: {sla_record.uptime_percentage}%, "
                f"avg response time: {sla_record.avg_response_time_ms}ms"
            )
            return {
                "success": True,
                "sla_id": sla_record.id,
                "uptime_percentage": sla_record.uptime_percentage,
                "avg_response_time_ms": sla_record.avg_response_time_ms
            }
        else:
            logger.warning("Monthly SLA report generation returned None")
            return {
                "success": False,
                "message": "No metrics data available"
            }

    except Exception as e:
        logger.error(f"Failed to generate monthly SLA report: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


# Celery Beat 调度配置（需要添加到 celery_app.py 的 beat_schedule 中）
"""
在 app/celery_app.py 的 celery_app.conf.beat_schedule 中添加：

'generate-hourly-sla': {
    'task': 'generate_hourly_sla_report',
    'schedule': crontab(minute=5),  # 每小时的第5分钟执行
},
'generate-daily-sla': {
    'task': 'generate_daily_sla_report',
    'schedule': crontab(hour=0, minute=10),  # 每天凌晨00:10执行
},
'generate-weekly-sla': {
    'task': 'generate_weekly_sla_report',
    'schedule': crontab(day_of_week=1, hour=0, minute=30),  # 每周一凌晨00:30执行
},
'generate-monthly-sla': {
    'task': 'generate_monthly_sla_report',
    'schedule': crontab(day_of_month=1, hour=1, minute=0),  # 每月1号凌晨01:00执行
},
"""
