"""
Admin Notification Service - 管理员通知服务
用于在应用中创建和发送管理员通知

使用方法:
    from app.utils.admin_notification_service import AdminNotificationService

    # 创建新用户注册通知
    await AdminNotificationService.notify_new_user_registration(
        db=db,
        user_id=new_user.id,
        username=new_user.username,
        email=new_user.email
    )
"""

import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import AdminNotification, NotificationType
from app.models.user import AdminUser
from app.utils.websocket_manager import manager

logger = logging.getLogger(__name__)


class AdminNotificationService:
    """管理员通知服务类"""

    @staticmethod
    async def create_admin_notification(
        db: AsyncSession,
        admin_user_id: Optional[int],
        type: str,
        title: str,
        content: str,
        severity: str = "info",
        related_type: Optional[str] = None,
        related_id: Optional[int] = None,
        link: Optional[str] = None,
        send_websocket: bool = True,
    ) -> AdminNotification:
        """
        创建管理员通知

        Args:
            db: 数据库会话
            admin_user_id: 接收通知的管理员ID (None表示广播给所有管理员)
            type: 通知类型
            title: 通知标题
            content: 通知内容
            severity: 严重程度 (info/warning/error/critical)
            related_type: 关联对象类型
            related_id: 关联对象ID
            link: 跳转链接
            send_websocket: 是否通过WebSocket发送实时通知

        Returns:
            创建的通知对象
        """
        try:
            notification = AdminNotification(
                admin_user_id=admin_user_id,
                type=type,
                title=title,
                content=content,
                severity=severity,
                related_type=related_type,
                related_id=related_id,
                link=link,
                is_read=False,
            )

            db.add(notification)
            await db.commit()
            await db.refresh(notification)

            logger.info(
                f"✅ 管理员通知已创建: admin_user_id={admin_user_id}, type={type}, severity={severity}"
            )

            # 通过WebSocket发送实时通知
            if send_websocket:
                await AdminNotificationService._send_websocket_notification(notification)

            return notification

        except Exception as e:
            logger.error(f"❌ 创建管理员通知失败: {str(e)}")
            await db.rollback()
            raise

    @staticmethod
    async def _send_websocket_notification(notification: AdminNotification):
        """通过WebSocket发送实时通知给管理员"""
        try:
            message = {
                "type": "admin_notification",
                "notification_id": notification.id,
                "notification_type": notification.type,
                "title": notification.title,
                "content": notification.content,
                "severity": notification.severity,
                "link": notification.link,
                "created_at": notification.created_at.isoformat(),
            }
            await manager.send_admin_message(message)
        except Exception as e:
            logger.error(f"WebSocket发送通知失败: {str(e)}")

    @staticmethod
    async def notify_new_user_registration(
        db: AsyncSession,
        user_id: int,
        username: str,
        email: str,
    ):
        """
        新用户注册通知

        Args:
            db: 数据库会话
            user_id: 新用户ID
            username: 用户名
            email: 邮箱
        """
        await AdminNotificationService.create_admin_notification(
            db=db,
            admin_user_id=None,  # 广播给所有管理员
            type=NotificationType.NEW_USER_REGISTRATION,
            title="新用户注册",
            content=f"新用户 {username} ({email}) 已注册",
            severity="info",
            related_type="user",
            related_id=user_id,
            link=f"/users/{user_id}",
        )

    @staticmethod
    async def notify_pending_comment_review(
        db: AsyncSession,
        comment_id: int,
        video_title: str,
        user_name: str,
        comment_preview: str,
    ):
        """
        待审核评论通知

        Args:
            db: 数据库会话
            comment_id: 评论ID
            video_title: 视频标题
            user_name: 评论者名称
            comment_preview: 评论预览（前50字）
        """
        preview = comment_preview[:50] + "..." if len(comment_preview) > 50 else comment_preview

        await AdminNotificationService.create_admin_notification(
            db=db,
            admin_user_id=None,
            type=NotificationType.PENDING_COMMENT_REVIEW,
            title="待审核评论",
            content=f'{user_name} 在《{video_title}》评论: {preview}',
            severity="info",
            related_type="comment",
            related_id=comment_id,
            link=f"/comments?comment_id={comment_id}",
        )

    @staticmethod
    async def notify_system_error(
        db: AsyncSession,
        error_type: str,
        error_message: str,
        error_id: Optional[int] = None,
    ):
        """
        系统错误告警通知

        Args:
            db: 数据库会话
            error_type: 错误类型
            error_message: 错误消息
            error_id: 错误日志ID
        """
        await AdminNotificationService.create_admin_notification(
            db=db,
            admin_user_id=None,
            type=NotificationType.SYSTEM_ERROR_ALERT,
            title="系统错误告警",
            content=f"{error_type}: {error_message[:100]}",
            severity="error",
            related_type="error_log",
            related_id=error_id,
            link=f"/logs?tab=error&error_id={error_id}" if error_id else "/logs?tab=error",
        )

    @staticmethod
    async def notify_storage_warning(
        db: AsyncSession,
        usage_percent: float,
        used_gb: float,
        total_gb: float,
    ):
        """
        存储空间警告通知

        Args:
            db: 数据库会话
            usage_percent: 使用百分比
            used_gb: 已用空间(GB)
            total_gb: 总空间(GB)
        """
        severity = "critical" if usage_percent >= 90 else "warning" if usage_percent >= 80 else "info"

        await AdminNotificationService.create_admin_notification(
            db=db,
            admin_user_id=None,
            type=NotificationType.STORAGE_WARNING,
            title="存储空间警告",
            content=f"存储空间使用率达到 {usage_percent:.1f}% ({used_gb:.1f}GB / {total_gb:.1f}GB)",
            severity=severity,
            link="/system-health",
        )

    @staticmethod
    async def notify_upload_failed(
        db: AsyncSession,
        filename: str,
        user_name: str,
        error_reason: str,
    ):
        """
        上传失败通知

        Args:
            db: 数据库会话
            filename: 文件名
            user_name: 上传用户名
            error_reason: 失败原因
        """
        await AdminNotificationService.create_admin_notification(
            db=db,
            admin_user_id=None,
            type=NotificationType.UPLOAD_FAILED,
            title="视频上传失败",
            content=f'用户 {user_name} 上传 "{filename}" 失败: {error_reason}',
            severity="warning",
            link="/logs?tab=error",
        )

    @staticmethod
    async def notify_video_processing_complete(
        db: AsyncSession,
        video_id: int,
        video_title: str,
        processing_type: str = "transcode",
    ):
        """
        视频处理完成通知

        Args:
            db: 数据库会话
            video_id: 视频ID
            video_title: 视频标题
            processing_type: 处理类型（transcode/thumbnail等）
        """
        await AdminNotificationService.create_admin_notification(
            db=db,
            admin_user_id=None,
            type=NotificationType.VIDEO_PROCESSING_COMPLETE,
            title="视频处理完成",
            content=f'视频《{video_title}》{processing_type}处理完成',
            severity="info",
            related_type="video",
            related_id=video_id,
            link=f"/videos/{video_id}",
        )

    @staticmethod
    async def notify_suspicious_activity(
        db: AsyncSession,
        activity_type: str,
        description: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
    ):
        """
        可疑活动通知

        Args:
            db: 数据库会话
            activity_type: 活动类型
            description: 描述
            user_id: 相关用户ID
            ip_address: IP地址
        """
        content = f"{activity_type}: {description}"
        if ip_address:
            content += f" (IP: {ip_address})"

        await AdminNotificationService.create_admin_notification(
            db=db,
            admin_user_id=None,
            type=NotificationType.SUSPICIOUS_ACTIVITY,
            title="可疑活动检测",
            content=content,
            severity="warning",
            related_type="user" if user_id else None,
            related_id=user_id,
            link=f"/users/{user_id}" if user_id else "/logs?tab=login",
        )

    @staticmethod
    async def mark_as_read(
        db: AsyncSession,
        notification_id: int,
        admin_user_id: int,
    ) -> bool:
        """
        标记通知为已读

        Args:
            db: 数据库会话
            notification_id: 通知ID
            admin_user_id: 管理员ID

        Returns:
            是否成功
        """
        try:
            from datetime import datetime, timezone

            query = select(AdminNotification).where(AdminNotification.id == notification_id)
            result = await db.execute(query)
            notification = result.scalar_one_or_none()

            if not notification:
                return False

            # 检查权限（如果通知指定了管理员）
            if notification.admin_user_id and notification.admin_user_id != admin_user_id:
                return False

            notification.is_read = True
            notification.read_at = datetime.now(timezone.utc)
            await db.commit()

            logger.info(f"通知 {notification_id} 已标记为已读 (admin: {admin_user_id})")
            return True

        except Exception as e:
            logger.error(f"标记通知为已读失败: {str(e)}")
            await db.rollback()
            return False

    @staticmethod
    async def get_unread_count(
        db: AsyncSession,
        admin_user_id: Optional[int] = None,
    ) -> int:
        """
        获取未读通知数量

        Args:
            db: 数据库会话
            admin_user_id: 管理员ID (None表示所有广播通知)

        Returns:
            未读数量
        """
        from sqlalchemy import and_, func, or_

        try:
            # 查询条件：未读 且 (广播给所有人 或 指定给该管理员)
            conditions = [AdminNotification.is_read.is_(False)]

            if admin_user_id:
                conditions.append(
                    or_(
                        AdminNotification.admin_user_id.is_(None),
                        AdminNotification.admin_user_id == admin_user_id,
                    )
                )
            else:
                conditions.append(AdminNotification.admin_user_id.is_(None))

            query = select(func.count(AdminNotification.id)).where(and_(*conditions))
            result = await db.execute(query)
            count = result.scalar() or 0

            return count

        except Exception as e:
            logger.error(f"获取未读通知数量失败: {str(e)}")
            return 0
