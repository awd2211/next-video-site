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
    async def notify_comment_moderation(
        db: AsyncSession,
        comment_id: int,
        action: str,
        video_title: str,
        admin_username: str,
        comment_count: int = 1,
    ):
        """
        评论审核操作通知

        Args:
            db: 数据库会话
            comment_id: 评论ID（单个操作）
            action: 操作类型 (approved/rejected/deleted)
            video_title: 视频标题
            admin_username: 执行操作的管理员
            comment_count: 评论数量（批量操作时 > 1）
        """
        action_map = {
            "approved": "已批准",
            "rejected": "已拒绝",
            "deleted": "已删除",
        }
        action_text = action_map.get(action, action)

        if comment_count > 1:
            title = f"批量评论{action_text}"
            content = f"管理员 {admin_username} {action_text} {comment_count} 条评论"
            link = "/comments"
        else:
            title = f"评论{action_text}"
            content = f'管理员 {admin_username} {action_text}《{video_title}》的评论'
            link = f"/comments?comment_id={comment_id}"

        severity = "info" if action == "approved" else "warning"

        await AdminNotificationService.create_admin_notification(
            db=db,
            admin_user_id=None,
            type="comment_moderation",
            title=title,
            content=content,
            severity=severity,
            related_type="comment",
            related_id=comment_id if comment_count == 1 else None,
            link=link,
        )

    @staticmethod
    async def notify_user_banned(
        db: AsyncSession,
        user_id: int,
        username: str,
        action: str,
        admin_username: str,
        user_count: int = 1,
    ):
        """
        用户封禁/解封通知

        Args:
            db: 数据库会话
            user_id: 用户ID
            username: 用户名
            action: 操作类型 (banned/unbanned)
            admin_username: 执行操作的管理员
            user_count: 用户数量（批量操作时 > 1）
        """
        action_map = {"banned": "已封禁", "unbanned": "已解封"}
        action_text = action_map.get(action, action)

        if user_count > 1:
            title = f"批量用户{action_text}"
            content = f"管理员 {admin_username} {action_text} {user_count} 个用户"
            link = "/users"
        else:
            title = f"用户{action_text}"
            content = f"管理员 {admin_username} {action_text}用户 {username}"
            link = f"/users/{user_id}"

        severity = "warning" if action == "banned" else "info"

        await AdminNotificationService.create_admin_notification(
            db=db,
            admin_user_id=None,
            type="user_management",
            title=title,
            content=content,
            severity=severity,
            related_type="user",
            related_id=user_id if user_count == 1 else None,
            link=link,
        )

    @staticmethod
    async def notify_batch_operation(
        db: AsyncSession,
        operation_type: str,
        entity_type: str,
        count: int,
        admin_username: str,
        details: Optional[str] = None,
    ):
        """
        批量操作通知

        Args:
            db: 数据库会话
            operation_type: 操作类型 (delete/update/approve/reject)
            entity_type: 实体类型 (video/comment/user)
            count: 操作数量
            admin_username: 执行操作的管理员
            details: 额外详情
        """
        operation_map = {
            "delete": "删除",
            "update": "更新",
            "approve": "批准",
            "reject": "拒绝",
        }
        entity_map = {"video": "视频", "comment": "评论", "user": "用户"}

        operation_text = operation_map.get(operation_type, operation_type)
        entity_text = entity_map.get(entity_type, entity_type)

        title = f"批量{operation_text}{entity_text}"
        content = f"管理员 {admin_username} {operation_text}了 {count} 个{entity_text}"
        if details:
            content += f" - {details}"

        severity = "warning" if operation_type == "delete" else "info"
        link = f"/{entity_type}s"

        await AdminNotificationService.create_admin_notification(
            db=db,
            admin_user_id=None,
            type="batch_operation",
            title=title,
            content=content,
            severity=severity,
            link=link,
        )

    @staticmethod
    async def notify_video_published(
        db: AsyncSession,
        video_id: int,
        video_title: str,
        admin_username: str,
    ):
        """
        视频发布通知

        Args:
            db: 数据库会话
            video_id: 视频ID
            video_title: 视频标题
            admin_username: 执行操作的管理员
        """
        await AdminNotificationService.create_admin_notification(
            db=db,
            admin_user_id=None,
            type="video_published",
            title="视频已发布",
            content=f'管理员 {admin_username} 发布了视频《{video_title}》',
            severity="info",
            related_type="video",
            related_id=video_id,
            link=f"/videos/{video_id}",
        )

    @staticmethod
    async def notify_announcement_management(
        db: AsyncSession,
        announcement_id: int,
        announcement_title: str,
        action: str,  # created/deleted/activated/deactivated
        admin_username: str,
    ):
        """
        公告管理通知

        Args:
            db: 数据库会话
            announcement_id: 公告ID
            announcement_title: 公告标题
            action: 操作类型
            admin_username: 执行操作的管理员
        """
        action_map = {
            "created": "创建",
            "deleted": "删除",
            "activated": "激活",
            "deactivated": "停用",
        }
        action_text = action_map.get(action, action)

        severity = "warning" if action == "deleted" else "info"

        await AdminNotificationService.create_admin_notification(
            db=db,
            admin_user_id=None,
            type="announcement_management",
            title=f"公告{action_text}",
            content=f'管理员 {admin_username} {action_text}了公告《{announcement_title}》',
            severity=severity,
            related_type="announcement",
            related_id=announcement_id,
            link=f"/announcements/{announcement_id}",
        )

    @staticmethod
    async def notify_banner_management(
        db: AsyncSession,
        banner_id: int,
        banner_title: str,
        action: str,  # created/deleted/activated/deactivated
        admin_username: str,
    ):
        """
        横幅管理通知

        Args:
            db: 数据库会话
            banner_id: 横幅ID
            banner_title: 横幅标题
            action: 操作类型
            admin_username: 执行操作的管理员
        """
        action_map = {
            "created": "创建",
            "deleted": "删除",
            "activated": "激活",
            "deactivated": "停用",
        }
        action_text = action_map.get(action, action)

        severity = "warning" if action == "deleted" else "info"

        await AdminNotificationService.create_admin_notification(
            db=db,
            admin_user_id=None,
            type="banner_management",
            title=f"横幅{action_text}",
            content=f'管理员 {admin_username} {action_text}了横幅《{banner_title}》',
            severity=severity,
            related_type="banner",
            related_id=banner_id,
            link=f"/banners/{banner_id}",
        )

    @staticmethod
    async def notify_ip_blacklist(
        db: AsyncSession,
        ip_address: str,
        action: str,  # added/removed
        admin_username: str,
        reason: Optional[str] = None,
        ip_count: int = 1,
    ):
        """
        IP黑名单管理通知

        Args:
            db: 数据库会话
            ip_address: IP地址
            action: 操作类型 (added/removed)
            admin_username: 执行操作的管理员
            reason: 封禁原因
            ip_count: IP数量（批量操作时 > 1）
        """
        action_map = {"added": "已封禁", "removed": "已解封"}
        action_text = action_map.get(action, action)

        if ip_count > 1:
            title = f"批量IP{action_text}"
            content = f"管理员 {admin_username} {action_text} {ip_count} 个IP地址"
        else:
            title = f"IP{action_text}"
            content = f"管理员 {admin_username} {action_text} IP: {ip_address}"
            if reason and action == "added":
                content += f" - 原因: {reason}"

        severity = "warning" if action == "added" else "info"

        await AdminNotificationService.create_admin_notification(
            db=db,
            admin_user_id=None,
            type="ip_blacklist",
            title=title,
            content=content,
            severity=severity,
            link="/ip-blacklist",
        )

    @staticmethod
    async def notify_series_management(
        db: AsyncSession,
        series_id: int,
        series_title: str,
        action: str,  # created/deleted/published/archived
        admin_username: str,
        series_count: int = 1,
    ):
        """
        专辑/系列管理通知

        Args:
            db: 数据库会话
            series_id: 专辑ID
            series_title: 专辑标题
            action: 操作类型
            admin_username: 执行操作的管理员
            series_count: 专辑数量（批量操作时 > 1）
        """
        action_map = {
            "created": "创建",
            "deleted": "删除",
            "published": "发布",
            "archived": "归档",
        }
        action_text = action_map.get(action, action)

        if series_count > 1:
            title = f"批量专辑{action_text}"
            content = f"管理员 {admin_username} {action_text}了 {series_count} 个专辑"
            link = "/series"
        else:
            title = f"专辑{action_text}"
            content = f'管理员 {admin_username} {action_text}了专辑《{series_title}》'
            link = f"/series/{series_id}"

        severity = "warning" if action == "deleted" else "info"

        await AdminNotificationService.create_admin_notification(
            db=db,
            admin_user_id=None,
            type="series_management",
            title=title,
            content=content,
            severity=severity,
            related_type="series",
            related_id=series_id if series_count == 1 else None,
            link=link,
        )

    @staticmethod
    async def notify_scheduled_content(
        db: AsyncSession,
        content_id: int,
        content_title: str,
        content_type: str,  # video/announcement/banner
        action: str,  # scheduled/cancelled/published
        scheduled_time: Optional[str] = None,
        admin_username: Optional[str] = None,
    ):
        """
        定时发布内容通知

        Args:
            db: 数据库会话
            content_id: 内容ID
            content_title: 内容标题
            content_type: 内容类型
            action: 操作类型
            scheduled_time: 定时发布时间
            admin_username: 执行操作的管理员
        """
        type_map = {"video": "视频", "announcement": "公告", "banner": "横幅"}
        action_map = {
            "scheduled": "已设置定时发布",
            "cancelled": "已取消定时发布",
            "published": "已自动发布",
        }

        type_text = type_map.get(content_type, content_type)
        action_text = action_map.get(action, action)

        if action == "scheduled":
            title = f"{type_text}定时发布"
            content = f'管理员 {admin_username} 为{type_text}《{content_title}》设置定时发布'
            if scheduled_time:
                content += f": {scheduled_time}"
            severity = "info"
        elif action == "cancelled":
            title = f"取消定时发布"
            content = f'管理员 {admin_username} 取消了{type_text}《{content_title}》的定时发布'
            severity = "info"
        else:  # published
            title = f"{type_text}自动发布"
            content = f'{type_text}《{content_title}》已按计划自动发布'
            severity = "info"

        await AdminNotificationService.create_admin_notification(
            db=db,
            admin_user_id=None,
            type="scheduled_content",
            title=title,
            content=content,
            severity=severity,
            related_type=content_type,
            related_id=content_id,
            link=f"/{content_type}s/{content_id}",
        )

    @staticmethod
    async def notify_danmaku_management(
        db: AsyncSession,
        danmaku_id: int,
        action: str,  # approved/rejected/deleted/blocked
        admin_username: str,
        video_title: Optional[str] = None,
        danmaku_count: int = 1,
    ):
        """
        弹幕管理通知

        Args:
            db: 数据库会话
            danmaku_id: 弹幕ID
            action: 操作类型
            admin_username: 执行操作的管理员
            video_title: 视频标题（可选）
            danmaku_count: 弹幕数量（批量操作时 > 1）
        """
        action_map = {
            "approved": "已批准",
            "rejected": "已拒绝",
            "deleted": "已删除",
            "blocked": "已屏蔽",
        }
        action_text = action_map.get(action, action)

        if danmaku_count > 1:
            title = f"批量弹幕{action_text}"
            content = f"管理员 {admin_username} {action_text} {danmaku_count} 条弹幕"
            link = "/danmaku"
        else:
            title = f"弹幕{action_text}"
            if video_title:
                content = f'管理员 {admin_username} {action_text}《{video_title}》的弹幕'
            else:
                content = f"管理员 {admin_username} {action_text}弹幕"
            link = f"/danmaku?danmaku_id={danmaku_id}"

        severity = "warning" if action in ["deleted", "blocked"] else "info"

        await AdminNotificationService.create_admin_notification(
            db=db,
            admin_user_id=None,
            type="danmaku_management",
            title=title,
            content=content,
            severity=severity,
            related_type="danmaku",
            related_id=danmaku_id if danmaku_count == 1 else None,
            link=link,
        )

    @staticmethod
    async def notify_rbac_management(
        db: AsyncSession,
        target_type: str,  # role/permission/admin_role_assignment
        target_id: int,
        target_name: str,
        action: str,  # created/updated/deleted/assigned/removed
        admin_username: str,
        details: Optional[str] = None,
    ):
        """
        RBAC权限管理通知

        Args:
            db: 数据库会话
            target_type: 目标类型 (role/permission/admin_role_assignment)
            target_id: 目标ID
            target_name: 目标名称
            action: 操作类型
            admin_username: 执行操作的管理员
            details: 额外详情
        """
        type_map = {
            "role": "角色",
            "permission": "权限",
            "admin_role_assignment": "管理员角色分配",
        }
        action_map = {
            "created": "创建",
            "updated": "更新",
            "deleted": "删除",
            "assigned": "分配",
            "removed": "移除",
        }

        type_text = type_map.get(target_type, target_type)
        action_text = action_map.get(action, action)

        title = f"{type_text}{action_text}"
        content = f'管理员 {admin_username} {action_text}了{type_text}《{target_name}》'
        if details:
            content += f" - {details}"

        severity = "warning" if action == "deleted" else "info"

        await AdminNotificationService.create_admin_notification(
            db=db,
            admin_user_id=None,
            type="rbac_management",
            title=title,
            content=content,
            severity=severity,
            related_type=target_type,
            related_id=target_id,
            link="/rbac/roles" if target_type == "role" else "/rbac/permissions",
        )

    @staticmethod
    async def notify_ai_provider_management(
        db: AsyncSession,
        provider_id: int,
        provider_name: str,
        action: str,  # created/updated/deleted/tested/enabled/disabled
        admin_username: str,
        details: Optional[str] = None,
    ):
        """
        AI提供商管理通知

        Args:
            db: 数据库会话
            provider_id: 提供商ID
            provider_name: 提供商名称
            action: 操作类型
            admin_username: 执行操作的管理员
            details: 额外详情（如测试结果）
        """
        action_map = {
            "created": "创建",
            "updated": "更新",
            "deleted": "删除",
            "tested": "测试",
            "enabled": "启用",
            "disabled": "禁用",
        }
        action_text = action_map.get(action, action)

        title = f"AI提供商{action_text}"
        content = f'管理员 {admin_username} {action_text}了AI提供商《{provider_name}》'
        if details:
            content += f" - {details}"

        severity = "warning" if action == "deleted" else "info"

        await AdminNotificationService.create_admin_notification(
            db=db,
            admin_user_id=None,
            type="ai_provider_management",
            title=title,
            content=content,
            severity=severity,
            related_type="ai_provider",
            related_id=provider_id,
            link=f"/ai-management/providers/{provider_id}",
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
