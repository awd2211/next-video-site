"""
Storage monitoring service to track MinIO storage usage
and send alerts when thresholds are exceeded
"""

import asyncio
from datetime import datetime, timezone
from typing import Optional

from loguru import logger

from app.database import async_session_maker
from app.utils.admin_notification_service import AdminNotificationService
from app.utils.minio_client import minio_client


class StorageMonitor:
    """Monitor storage usage and send notifications"""

    # Storage thresholds (percentage)
    WARNING_THRESHOLD = 80  # 80% usage triggers warning
    CRITICAL_THRESHOLD = 90  # 90% usage triggers critical alert

    # Cooldown period (seconds) to avoid notification spam
    NOTIFICATION_COOLDOWN = 3600  # 1 hour

    def __init__(self):
        self.last_notification_time: Optional[datetime] = None
        self.last_notification_level: Optional[str] = None

    async def check_storage_usage(self) -> dict:
        """
        Check current storage usage from MinIO

        Returns:
            dict: Storage statistics including used_gb, total_gb, usage_percent
        """
        try:
            # Get MinIO client statistics
            # Note: This is a simplified implementation
            # In production, you would query actual MinIO metrics
            bucket_name = minio_client.bucket_name

            # Get list of objects and calculate total size
            objects = minio_client.client.list_objects(bucket_name, recursive=True)
            total_size = sum(obj.size for obj in objects)

            # Convert to GB
            used_gb = round(total_size / (1024**3), 2)

            # For demo purposes, assume 1TB total capacity
            # In production, query actual storage capacity from MinIO/system
            total_gb = 1000  # 1TB

            usage_percent = round((used_gb / total_gb) * 100, 2)

            return {
                "used_gb": used_gb,
                "total_gb": total_gb,
                "usage_percent": usage_percent,
                "available_gb": round(total_gb - used_gb, 2),
                "timestamp": datetime.now(timezone.utc),
            }

        except Exception as e:
            logger.error(f"Failed to check storage usage: {e}")
            return {
                "used_gb": 0,
                "total_gb": 0,
                "usage_percent": 0,
                "available_gb": 0,
                "timestamp": datetime.now(timezone.utc),
                "error": str(e),
            }

    async def should_send_notification(
        self, usage_percent: float, severity: str
    ) -> bool:
        """
        Determine if a notification should be sent based on cooldown and severity

        Args:
            usage_percent: Current storage usage percentage
            severity: Notification severity (warning or critical)

        Returns:
            bool: True if notification should be sent
        """
        now = datetime.now(timezone.utc)

        # Always send if no previous notification
        if self.last_notification_time is None:
            return True

        # Calculate time since last notification
        time_since_last = (now - self.last_notification_time).total_seconds()

        # If cooldown period hasn't passed, don't send
        if time_since_last < self.NOTIFICATION_COOLDOWN:
            return False

        # If severity escalated (warning -> critical), send immediately
        if (
            severity == "critical"
            and self.last_notification_level == "warning"
            and time_since_last > 300
        ):  # At least 5 min between
            return True

        # Otherwise, respect cooldown
        return time_since_last >= self.NOTIFICATION_COOLDOWN

    async def monitor_and_notify(self):
        """
        Check storage usage and send notifications if thresholds exceeded
        """
        async with async_session_maker() as db:
            try:
                # Check storage usage
                stats = await self.check_storage_usage()

                if "error" in stats:
                    logger.warning(f"Storage check failed: {stats['error']}")
                    return

                usage_percent = stats["usage_percent"]
                used_gb = stats["used_gb"]
                total_gb = stats["total_gb"]

                # Determine severity level
                severity = None
                if usage_percent >= self.CRITICAL_THRESHOLD:
                    severity = "critical"
                elif usage_percent >= self.WARNING_THRESHOLD:
                    severity = "warning"

                # Send notification if threshold exceeded
                if severity and await self.should_send_notification(
                    usage_percent, severity
                ):
                    await AdminNotificationService.notify_storage_warning(
                        db=db,
                        usage_percent=usage_percent,
                        used_gb=used_gb,
                        total_gb=total_gb,
                    )

                    self.last_notification_time = datetime.now(timezone.utc)
                    self.last_notification_level = severity

                    logger.info(
                        f"Storage {severity} notification sent: {usage_percent}% used"
                    )
                else:
                    logger.debug(f"Storage usage OK: {usage_percent}%")

            except Exception as e:
                logger.error(f"Storage monitoring error: {e}")

    async def start_monitoring(self, interval: int = 3600):
        """
        Start continuous storage monitoring

        Args:
            interval: Check interval in seconds (default: 1 hour)
        """
        logger.info(f"Starting storage monitoring (interval: {interval}s)")

        while True:
            try:
                await self.monitor_and_notify()
            except Exception as e:
                logger.error(f"Storage monitoring loop error: {e}")

            # Wait for next check
            await asyncio.sleep(interval)


# Global storage monitor instance
storage_monitor = StorageMonitor()


async def start_storage_monitoring():
    """
    Start storage monitoring in background task
    This should be called from app startup event
    """
    # Check immediately on startup
    await storage_monitor.monitor_and_notify()

    # Then start periodic monitoring
    # Run every hour by default
    asyncio.create_task(storage_monitor.start_monitoring(interval=3600))
