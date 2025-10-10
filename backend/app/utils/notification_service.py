"""
通知服务 - 用于在应用中创建和发送通知

使用方法:
    from app.utils.notification_service import NotificationService

    # 在其他API中创建通知
    await NotificationService.create_notification(
        db=db,
        user_id=target_user_id,
        type="comment_reply",
        title="有人回复了你的评论",
        content=f"{replier_name} 回复了你: {reply_content}",
        related_type="comment",
        related_id=comment_id,
        link=f"/videos/{video_id}?comment={comment_id}"
    )
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification, NotificationType
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """通知服务类"""

    @staticmethod
    async def create_notification(
        db: AsyncSession,
        user_id: int,
        type: str,
        title: str,
        content: str,
        related_type: Optional[str] = None,
        related_id: Optional[int] = None,
        link: Optional[str] = None,
    ) -> Notification:
        """
        创建通知

        Args:
            db: 数据库会话
            user_id: 接收通知的用户ID
            type: 通知类型
            title: 通知标题
            content: 通知内容
            related_type: 关联对象类型 (video, comment, user等)
            related_id: 关联对象ID
            link: 跳转链接

        Returns:
            创建的通知对象
        """
        try:
            notification = Notification(
                user_id=user_id,
                type=type,
                title=title,
                content=content,
                related_type=related_type,
                related_id=related_id,
                link=link,
                is_read=False,
            )

            db.add(notification)
            await db.commit()
            await db.refresh(notification)

            logger.info(
                f"✅ 通知已创建: user_id={user_id}, type={type}, title={title}"
            )

            return notification

        except Exception as e:
            logger.error(f"❌ 创建通知失败: {str(e)}")
            await db.rollback()
            raise

    @staticmethod
    async def notify_comment_reply(
        db: AsyncSession,
        target_user_id: int,
        replier_name: str,
        reply_content: str,
        video_id: int,
        comment_id: int,
    ):
        """
        评论回复通知

        Args:
            db: 数据库会话
            target_user_id: 被回复的用户ID
            replier_name: 回复者名称
            reply_content: 回复内容
            video_id: 视频ID
            comment_id: 评论ID
        """
        # 截断过长的回复内容
        preview = reply_content[:50] + "..." if len(reply_content) > 50 else reply_content

        await NotificationService.create_notification(
            db=db,
            user_id=target_user_id,
            type=NotificationType.COMMENT_REPLY,
            title="有人回复了你的评论",
            content=f"{replier_name} 回复了你: {preview}",
            related_type="comment",
            related_id=comment_id,
            link=f"/videos/{video_id}?comment={comment_id}",
        )

    @staticmethod
    async def notify_video_published(
        db: AsyncSession,
        user_id: int,
        video_title: str,
        video_id: int,
    ):
        """
        视频发布通知 (可用于关注的UP主发布新视频)

        Args:
            db: 数据库会话
            user_id: 接收通知的用户ID
            video_title: 视频标题
            video_id: 视频ID
        """
        await NotificationService.create_notification(
            db=db,
            user_id=user_id,
            type=NotificationType.VIDEO_PUBLISHED,
            title="你关注的UP主发布了新视频",
            content=f"《{video_title}》",
            related_type="video",
            related_id=video_id,
            link=f"/videos/{video_id}",
        )

    @staticmethod
    async def notify_system_announcement(
        db: AsyncSession,
        user_ids: list[int],
        title: str,
        content: str,
        link: Optional[str] = None,
    ):
        """
        系统公告通知 (批量发送)

        Args:
            db: 数据库会话
            user_ids: 接收通知的用户ID列表
            title: 公告标题
            content: 公告内容
            link: 跳转链接 (可选)
        """
        notifications = []

        for user_id in user_ids:
            notification = Notification(
                user_id=user_id,
                type=NotificationType.SYSTEM_ANNOUNCEMENT,
                title=title,
                content=content,
                link=link,
                is_read=False,
            )
            notifications.append(notification)

        try:
            db.add_all(notifications)
            await db.commit()

            logger.info(
                f"✅ 批量系统公告已发送: {len(notifications)} 条通知"
            )

        except Exception as e:
            logger.error(f"❌ 批量发送系统公告失败: {str(e)}")
            await db.rollback()
            raise

    @staticmethod
    async def notify_video_recommendation(
        db: AsyncSession,
        user_id: int,
        video_title: str,
        video_id: int,
        reason: str = "根据你的观看历史推荐",
    ):
        """
        视频推荐通知

        Args:
            db: 数据库会话
            user_id: 接收通知的用户ID
            video_title: 视频标题
            video_id: 视频ID
            reason: 推荐理由
        """
        await NotificationService.create_notification(
            db=db,
            user_id=user_id,
            type=NotificationType.VIDEO_RECOMMENDATION,
            title="为你推荐",
            content=f"《{video_title}》 - {reason}",
            related_type="video",
            related_id=video_id,
            link=f"/videos/{video_id}",
        )
