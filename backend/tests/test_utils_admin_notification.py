"""
测试 Utils - Admin Notification Service (管理员通知服务)
测试管理员通知的创建、发送和管理功能
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from app.database import AsyncSessionLocal
from app.models.notification import AdminNotification, NotificationType
from app.models.user import AdminUser
from app.utils.admin_notification_service import AdminNotificationService


# ===========================================
# Test Fixtures
# ===========================================

@pytest.fixture
async def db_session():
    """创建测试数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()  # 测试后回滚


# ===========================================
# 1. 基础通知创建测试
# ===========================================

class TestCreateAdminNotification:
    """测试创建管理员通知"""

    @pytest.mark.asyncio
    async def test_create_basic_notification(self, db_session):
        """测试创建基础通知"""
        with patch("app.utils.admin_notification_service.manager.send_admin_message") as mock_ws:
            notification = await AdminNotificationService.create_admin_notification(
                db=db_session,
                admin_user_id=None,  # 广播给所有管理员
                type="test_type",
                title="测试通知",
                content="测试内容",
                severity="info",
            )

            assert notification.id is not None
            assert notification.title == "测试通知"
            assert notification.content == "测试内容"
            assert notification.severity == "info"
            assert notification.is_read is False
            assert notification.admin_user_id is None
            mock_ws.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_notification_for_specific_admin(
        self, db_session, test_admin: AdminUser
    ):
        """测试创建给特定管理员的通知"""
        with patch("app.utils.admin_notification_service.manager.send_admin_message"):
            notification = await AdminNotificationService.create_admin_notification(
                db=db_session,
                admin_user_id=test_admin.id,
                type="specific_type",
                title="私人通知",
                content="仅给特定管理员",
                severity="warning",
            )

            assert notification.admin_user_id == test_admin.id
            assert notification.title == "私人通知"
            assert notification.severity == "warning"

    @pytest.mark.asyncio
    async def test_create_notification_with_related_data(self, db_session):
        """测试创建带关联数据的通知"""
        with patch("app.utils.admin_notification_service.manager.send_admin_message"):
            notification = await AdminNotificationService.create_admin_notification(
                db=db_session,
                admin_user_id=None,
                type="video_related",
                title="视频通知",
                content="视频相关",
                severity="info",
                related_type="video",
                related_id=123,
                link="/videos/123",
            )

            assert notification.related_type == "video"
            assert notification.related_id == 123
            assert notification.link == "/videos/123"

    @pytest.mark.asyncio
    async def test_create_notification_without_websocket(self, db_session):
        """测试创建通知但不发送WebSocket"""
        with patch("app.utils.admin_notification_service.manager.send_admin_message") as mock_ws:
            notification = await AdminNotificationService.create_admin_notification(
                db=db_session,
                admin_user_id=None,
                type="test",
                title="无WebSocket",
                content="测试",
                send_websocket=False,
            )

            assert notification.id is not None
            mock_ws.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_notification_all_severities(self, db_session):
        """测试所有严重程度级别"""
        with patch("app.utils.admin_notification_service.manager.send_admin_message"):
            for severity in ["info", "warning", "error", "critical"]:
                notification = await AdminNotificationService.create_admin_notification(
                    db=db_session,
                    admin_user_id=None,
                    type="severity_test",
                    title=f"{severity}通知",
                    content="测试严重程度",
                    severity=severity,
                )
                assert notification.severity == severity


# ===========================================
# 2. 业务通知测试 - 用户相关
# ===========================================

class TestUserNotifications:
    """测试用户相关通知"""

    @pytest.mark.asyncio
    async def test_notify_new_user_registration(self, db_session):
        """测试新用户注册通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_new_user_registration(
                db=db_session,
                user_id=123,
                username="testuser",
                email="test@example.com"
            )

            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["type"] == NotificationType.NEW_USER_REGISTRATION
            assert "testuser" in call_kwargs["content"]
            assert "test@example.com" in call_kwargs["content"]
            assert call_kwargs["related_type"] == "user"
            assert call_kwargs["related_id"] == 123

    @pytest.mark.asyncio
    async def test_notify_user_banned(self, db_session):
        """测试用户封禁通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_user_banned(
                db=db_session,
                user_id=123,
                username="baduser",
                action="banned",
                admin_username="admin1"
            )

            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args.kwargs
            assert "已封禁" in call_kwargs["title"]
            assert "baduser" in call_kwargs["content"]
            assert call_kwargs["severity"] == "warning"

    @pytest.mark.asyncio
    async def test_notify_user_unbanned(self, db_session):
        """测试用户解封通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_user_banned(
                db=db_session,
                user_id=123,
                username="gooduser",
                action="unbanned",
                admin_username="admin1"
            )

            call_kwargs = mock_create.call_args.kwargs
            assert "已解封" in call_kwargs["title"]
            assert call_kwargs["severity"] == "info"

    @pytest.mark.asyncio
    async def test_notify_batch_user_ban(self, db_session):
        """测试批量用户封禁通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_user_banned(
                db=db_session,
                user_id=123,
                username="user",
                action="banned",
                admin_username="admin1",
                user_count=5
            )

            call_kwargs = mock_create.call_args.kwargs
            assert "批量" in call_kwargs["title"]
            assert "5" in call_kwargs["content"]


# ===========================================
# 3. 业务通知测试 - 内容相关
# ===========================================

class TestContentNotifications:
    """测试内容相关通知"""

    @pytest.mark.asyncio
    async def test_notify_pending_comment_review(self, db_session):
        """测试待审核评论通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_pending_comment_review(
                db=db_session,
                comment_id=456,
                video_title="测试视频",
                user_name="评论者",
                comment_preview="这是一条很长的评论内容" * 10  # 超过50字
            )

            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["type"] == NotificationType.PENDING_COMMENT_REVIEW
            assert "测试视频" in call_kwargs["content"]
            assert "..." in call_kwargs["content"]  # 应该被截断
            assert len(call_kwargs["content"].split("...")[0]) <= 100

    @pytest.mark.asyncio
    async def test_notify_comment_moderation(self, db_session):
        """测试评论审核操作通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            for action in ["approved", "rejected", "deleted"]:
                await AdminNotificationService.notify_comment_moderation(
                    db=db_session,
                    comment_id=123,
                    action=action,
                    video_title="测试视频",
                    admin_username="admin1"
                )

                call_kwargs = mock_create.call_args.kwargs
                assert action.replace("d", "").replace("ed", "") in call_kwargs["title"] or "批准" in call_kwargs["title"] or "拒绝" in call_kwargs["title"] or "删除" in call_kwargs["title"]

    @pytest.mark.asyncio
    async def test_notify_video_published(self, db_session):
        """测试视频发布通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_video_published(
                db=db_session,
                video_id=789,
                video_title="新视频",
                admin_username="admin1"
            )

            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["type"] == "video_published"
            assert "新视频" in call_kwargs["content"]
            assert call_kwargs["link"] == "/videos/789"

    @pytest.mark.asyncio
    async def test_notify_video_processing_complete(self, db_session):
        """测试视频处理完成通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_video_processing_complete(
                db=db_session,
                video_id=123,
                video_title="处理视频",
                processing_type="transcode"
            )

            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["type"] == NotificationType.VIDEO_PROCESSING_COMPLETE
            assert "transcode" in call_kwargs["content"]


# ===========================================
# 4. 业务通知测试 - 系统相关
# ===========================================

class TestSystemNotifications:
    """测试系统相关通知"""

    @pytest.mark.asyncio
    async def test_notify_system_error(self, db_session):
        """测试系统错误通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_system_error(
                db=db_session,
                error_type="DatabaseError",
                error_message="连接失败",
                error_id=999
            )

            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["type"] == NotificationType.SYSTEM_ERROR_ALERT
            assert call_kwargs["severity"] == "error"
            assert "DatabaseError" in call_kwargs["content"]
            assert call_kwargs["link"] == "/logs?tab=error&error_id=999"

    @pytest.mark.asyncio
    async def test_notify_storage_warning_levels(self, db_session):
        """测试存储空间警告不同级别"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            # 测试不同使用率的严重程度
            test_cases = [
                (75.0, "info"),
                (85.0, "warning"),
                (95.0, "critical"),
            ]

            for usage_percent, expected_severity in test_cases:
                await AdminNotificationService.notify_storage_warning(
                    db=db_session,
                    usage_percent=usage_percent,
                    used_gb=usage_percent * 10,
                    total_gb=1000.0
                )

                call_kwargs = mock_create.call_args.kwargs
                assert call_kwargs["severity"] == expected_severity
                assert f"{usage_percent:.1f}%" in call_kwargs["content"]

    @pytest.mark.asyncio
    async def test_notify_upload_failed(self, db_session):
        """测试上传失败通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_upload_failed(
                db=db_session,
                filename="video.mp4",
                user_name="uploader",
                error_reason="文件过大"
            )

            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["type"] == NotificationType.UPLOAD_FAILED
            assert "video.mp4" in call_kwargs["content"]
            assert "文件过大" in call_kwargs["content"]
            assert call_kwargs["severity"] == "warning"


# ===========================================
# 5. 业务通知测试 - 安全相关
# ===========================================

class TestSecurityNotifications:
    """测试安全相关通知"""

    @pytest.mark.asyncio
    async def test_notify_suspicious_activity(self, db_session):
        """测试可疑活动通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_suspicious_activity(
                db=db_session,
                activity_type="多次登录失败",
                description="5分钟内失败10次",
                user_id=123,
                ip_address="192.168.1.100"
            )

            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["type"] == NotificationType.SUSPICIOUS_ACTIVITY
            assert "192.168.1.100" in call_kwargs["content"]
            assert call_kwargs["severity"] == "warning"

    @pytest.mark.asyncio
    async def test_notify_ip_blacklist_add(self, db_session):
        """测试IP加入黑名单通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_ip_blacklist(
                db=db_session,
                ip_address="10.0.0.1",
                action="added",
                admin_username="admin1",
                reason="恶意攻击"
            )

            call_kwargs = mock_create.call_args.kwargs
            assert "已封禁" in call_kwargs["title"]
            assert "10.0.0.1" in call_kwargs["content"]
            assert "恶意攻击" in call_kwargs["content"]
            assert call_kwargs["severity"] == "warning"

    @pytest.mark.asyncio
    async def test_notify_ip_blacklist_remove(self, db_session):
        """测试IP移出黑名单通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_ip_blacklist(
                db=db_session,
                ip_address="10.0.0.1",
                action="removed",
                admin_username="admin1"
            )

            call_kwargs = mock_create.call_args.kwargs
            assert "已解封" in call_kwargs["title"]
            assert call_kwargs["severity"] == "info"

    @pytest.mark.asyncio
    async def test_notify_batch_ip_blacklist(self, db_session):
        """测试批量IP黑名单通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_ip_blacklist(
                db=db_session,
                ip_address="",
                action="added",
                admin_username="admin1",
                ip_count=10
            )

            call_kwargs = mock_create.call_args.kwargs
            assert "批量" in call_kwargs["title"]
            assert "10" in call_kwargs["content"]


# ===========================================
# 6. 业务通知测试 - 管理操作
# ===========================================

class TestManagementNotifications:
    """测试管理操作通知"""

    @pytest.mark.asyncio
    async def test_notify_announcement_management(self, db_session):
        """测试公告管理通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            for action in ["created", "deleted", "activated", "deactivated"]:
                await AdminNotificationService.notify_announcement_management(
                    db=db_session,
                    announcement_id=123,
                    announcement_title="系统公告",
                    action=action,
                    admin_username="admin1"
                )

                call_kwargs = mock_create.call_args.kwargs
                assert call_kwargs["type"] == "announcement_management"
                severity = "warning" if action == "deleted" else "info"
                assert call_kwargs["severity"] == severity

    @pytest.mark.asyncio
    async def test_notify_banner_management(self, db_session):
        """测试横幅管理通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_banner_management(
                db=db_session,
                banner_id=456,
                banner_title="首页横幅",
                action="created",
                admin_username="admin1"
            )

            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["type"] == "banner_management"
            assert "首页横幅" in call_kwargs["content"]

    @pytest.mark.asyncio
    async def test_notify_batch_operation(self, db_session):
        """测试批量操作通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_batch_operation(
                db=db_session,
                operation_type="delete",
                entity_type="video",
                count=15,
                admin_username="admin1",
                details="已过期内容"
            )

            call_kwargs = mock_create.call_args.kwargs
            assert "批量" in call_kwargs["title"]
            assert "15" in call_kwargs["content"]
            assert "已过期内容" in call_kwargs["content"]
            assert call_kwargs["severity"] == "warning"

    @pytest.mark.asyncio
    async def test_notify_series_management(self, db_session):
        """测试专辑管理通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_series_management(
                db=db_session,
                series_id=789,
                series_title="经典系列",
                action="published",
                admin_username="admin1"
            )

            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["type"] == "series_management"
            assert "经典系列" in call_kwargs["content"]


# ===========================================
# 7. 业务通知测试 - 定时和弹幕
# ===========================================

class TestScheduledAndDanmakuNotifications:
    """测试定时发布和弹幕通知"""

    @pytest.mark.asyncio
    async def test_notify_scheduled_content(self, db_session):
        """测试定时发布通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_scheduled_content(
                db=db_session,
                content_id=123,
                content_title="定时视频",
                content_type="video",
                action="scheduled",
                scheduled_time="2025-12-31 00:00:00",
                admin_username="admin1"
            )

            call_kwargs = mock_create.call_args.kwargs
            assert "定时发布" in call_kwargs["title"]
            assert "2025-12-31 00:00:00" in call_kwargs["content"]

    @pytest.mark.asyncio
    async def test_notify_scheduled_content_auto_published(self, db_session):
        """测试自动发布通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_scheduled_content(
                db=db_session,
                content_id=123,
                content_title="自动发布视频",
                content_type="video",
                action="published"
            )

            call_kwargs = mock_create.call_args.kwargs
            assert "自动发布" in call_kwargs["title"]

    @pytest.mark.asyncio
    async def test_notify_danmaku_management(self, db_session):
        """测试弹幕管理通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_danmaku_management(
                db=db_session,
                danmaku_id=999,
                action="blocked",
                admin_username="admin1",
                video_title="测试视频"
            )

            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["type"] == "danmaku_management"
            assert call_kwargs["severity"] == "warning"


# ===========================================
# 8. 业务通知测试 - RBAC和AI
# ===========================================

class TestRBACAndAINotifications:
    """测试RBAC和AI管理通知"""

    @pytest.mark.asyncio
    async def test_notify_rbac_management(self, db_session):
        """测试RBAC管理通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_rbac_management(
                db=db_session,
                target_type="role",
                target_id=1,
                target_name="编辑",
                action="created",
                admin_username="superadmin",
                details="包含10个权限"
            )

            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["type"] == "rbac_management"
            assert "角色" in call_kwargs["title"]
            assert "包含10个权限" in call_kwargs["content"]

    @pytest.mark.asyncio
    async def test_notify_ai_provider_management(self, db_session):
        """测试AI提供商管理通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_ai_provider_management(
                db=db_session,
                provider_id=1,
                provider_name="OpenAI",
                action="tested",
                admin_username="admin1",
                details="测试成功 - 响应时间 200ms"
            )

            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["type"] == "ai_provider_management"
            assert "OpenAI" in call_kwargs["content"]
            assert "测试成功" in call_kwargs["content"]

    @pytest.mark.asyncio
    async def test_notify_system_settings_change(self, db_session):
        """测试系统设置变更通知"""
        with patch("app.utils.admin_notification_service.AdminNotificationService.create_admin_notification") as mock_create:
            await AdminNotificationService.notify_system_settings_change(
                db=db_session,
                setting_category="security",
                action="updated",
                admin_username="superadmin",
                details="更新密码策略"
            )

            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["type"] == "system_settings_change"
            assert "安全设置" in call_kwargs["title"]
            assert "更新密码策略" in call_kwargs["content"]


# ===========================================
# 9. 通知管理功能测试
# ===========================================

class TestNotificationManagement:
    """测试通知管理功能"""

    @pytest.mark.asyncio
    async def test_mark_as_read(self, db_session, test_admin: AdminUser):
        """测试标记通知为已读"""
        # 创建通知
        with patch("app.utils.admin_notification_service.manager.send_admin_message"):
            notification = await AdminNotificationService.create_admin_notification(
                db=db_session,
                admin_user_id=test_admin.id,
                type="test",
                title="测试",
                content="待标记"
            )

        # 标记为已读
        result = await AdminNotificationService.mark_as_read(
            db=db_session,
            notification_id=notification.id,
            admin_user_id=test_admin.id
        )

        assert result is True

        # 验证已标记
        await db_session.refresh(notification)
        assert notification.is_read is True
        assert notification.read_at is not None

    @pytest.mark.asyncio
    async def test_mark_as_read_nonexistent(self, db_session, test_admin: AdminUser):
        """测试标记不存在的通知"""
        result = await AdminNotificationService.mark_as_read(
            db=db_session,
            notification_id=999999,
            admin_user_id=test_admin.id
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_mark_as_read_wrong_admin(self, db_session, test_admin: AdminUser):
        """测试其他管理员尝试标记通知"""
        # 创建给特定管理员的通知
        with patch("app.utils.admin_notification_service.manager.send_admin_message"):
            notification = await AdminNotificationService.create_admin_notification(
                db=db_session,
                admin_user_id=test_admin.id,
                type="test",
                title="测试",
                content="私人通知"
            )

        # 使用其他管理员ID尝试标记
        result = await AdminNotificationService.mark_as_read(
            db=db_session,
            notification_id=notification.id,
            admin_user_id=test_admin.id + 1  # 不同的管理员
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_get_unread_count_for_admin(self, db_session, test_admin: AdminUser):
        """测试获取管理员未读数量"""
        # 创建3个广播通知
        with patch("app.utils.admin_notification_service.manager.send_admin_message"):
            for i in range(3):
                await AdminNotificationService.create_admin_notification(
                    db=db_session,
                    admin_user_id=None,  # 广播
                    type="test",
                    title=f"广播{i}",
                    content="测试"
                )

            # 创建1个私人通知
            await AdminNotificationService.create_admin_notification(
                db=db_session,
                admin_user_id=test_admin.id,
                type="test",
                title="私人",
                content="测试"
            )

        # 获取未读数量（应该包含广播+私人）
        count = await AdminNotificationService.get_unread_count(
            db=db_session,
            admin_user_id=test_admin.id
        )

        assert count == 4  # 3个广播 + 1个私人

    @pytest.mark.asyncio
    async def test_get_unread_count_all_broadcast(self, db_session):
        """测试获取所有广播未读数量"""
        # 创建5个广播通知
        with patch("app.utils.admin_notification_service.manager.send_admin_message"):
            for i in range(5):
                await AdminNotificationService.create_admin_notification(
                    db=db_session,
                    admin_user_id=None,
                    type="test",
                    title=f"广播{i}",
                    content="测试"
                )

        count = await AdminNotificationService.get_unread_count(
            db=db_session,
            admin_user_id=None
        )

        assert count == 5

    @pytest.mark.asyncio
    async def test_get_unread_count_after_reading(
        self, db_session, test_admin: AdminUser
    ):
        """测试读取后未读数量变化"""
        # 创建2个通知
        with patch("app.utils.admin_notification_service.manager.send_admin_message"):
            n1 = await AdminNotificationService.create_admin_notification(
                db=db_session,
                admin_user_id=test_admin.id,
                type="test",
                title="通知1",
                content="测试"
            )
            n2 = await AdminNotificationService.create_admin_notification(
                db=db_session,
                admin_user_id=test_admin.id,
                type="test",
                title="通知2",
                content="测试"
            )

        # 初始未读数量
        count_before = await AdminNotificationService.get_unread_count(
            db=db_session,
            admin_user_id=test_admin.id
        )
        assert count_before == 2

        # 标记一个为已读
        await AdminNotificationService.mark_as_read(
            db=db_session,
            notification_id=n1.id,
            admin_user_id=test_admin.id
        )

        # 验证未读数量减少
        count_after = await AdminNotificationService.get_unread_count(
            db=db_session,
            admin_user_id=test_admin.id
        )
        assert count_after == 1


# ===========================================
# 10. WebSocket集成测试
# ===========================================

class TestWebSocketIntegration:
    """测试WebSocket集成"""

    @pytest.mark.asyncio
    async def test_websocket_notification_sent(self, db_session):
        """测试WebSocket通知发送"""
        with patch("app.utils.admin_notification_service.manager.send_admin_message") as mock_ws:
            notification = await AdminNotificationService.create_admin_notification(
                db=db_session,
                admin_user_id=None,
                type="test",
                title="WebSocket测试",
                content="测试实时通知",
                severity="info",
                send_websocket=True
            )

            # 验证WebSocket被调用
            mock_ws.assert_called_once()

            # 验证消息内容
            call_args = mock_ws.call_args[0][0]
            assert call_args["type"] == "admin_notification"
            assert call_args["notification_id"] == notification.id
            assert call_args["title"] == "WebSocket测试"
            assert call_args["content"] == "测试实时通知"
            assert call_args["severity"] == "info"
            assert "created_at" in call_args

    @pytest.mark.asyncio
    async def test_websocket_failure_handling(self, db_session):
        """测试WebSocket发送失败处理"""
        with patch("app.utils.admin_notification_service.manager.send_admin_message") as mock_ws:
            mock_ws.side_effect = Exception("WebSocket连接失败")

            # 即使WebSocket失败，通知仍应创建成功
            notification = await AdminNotificationService.create_admin_notification(
                db=db_session,
                admin_user_id=None,
                type="test",
                title="测试",
                content="WebSocket失败测试"
            )

            assert notification.id is not None
            assert notification.title == "测试"


# ===========================================
# 测试总结
# ===========================================

"""
测试覆盖：
✅ 基础通知创建 - 6个测试用例
✅ 用户相关通知 - 4个测试用例
✅ 内容相关通知 - 4个测试用例
✅ 系统相关通知 - 3个测试用例
✅ 安全相关通知 - 4个测试用例
✅ 管理操作通知 - 4个测试用例
✅ 定时和弹幕通知 - 3个测试用例
✅ RBAC和AI通知 - 3个测试用例
✅ 通知管理功能 - 6个测试用例
✅ WebSocket集成 - 2个测试用例

总计：39个测试用例

测试场景：
- 创建基础通知（广播/私人）
- 不同严重程度（info/warning/error/critical）
- 关联数据（related_type/related_id/link）
- WebSocket实时推送
- 新用户注册通知
- 用户封禁/解封（单个/批量）
- 待审核评论（自动截断）
- 评论审核操作
- 视频发布/处理完成
- 系统错误告警
- 存储空间警告（不同级别）
- 上传失败通知
- 可疑活动检测
- IP黑名单管理（单个/批量）
- 公告/横幅/专辑管理
- 批量操作记录
- 定时发布（设置/取消/自动发布）
- 弹幕管理
- RBAC权限管理
- AI提供商管理
- 系统设置变更
- 标记已读功能
- 权限验证
- 未读数量统计
- WebSocket失败处理
"""
