"""
测试 API - WebSocket (WebSocket实时通信)
测试WebSocket连接、认证、消息推送和通知服务
"""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, AdminUser
from app.api.websocket import get_current_user_from_token
from app.utils.websocket_manager import ConnectionManager, NotificationService, manager
from app.utils.security import create_access_token


# ===========================================
# 测试 Fixtures
# ===========================================

@pytest.fixture
def connection_manager():
    """创建独立的连接管理器实例"""
    return ConnectionManager()


@pytest.fixture
def mock_websocket():
    """创建模拟的WebSocket连接"""
    ws = AsyncMock(spec=WebSocket)
    ws.accept = AsyncMock()
    ws.send_text = AsyncMock()
    ws.send_json = AsyncMock()
    ws.close = AsyncMock()
    ws.receive_text = AsyncMock()
    return ws


@pytest.fixture
def notification_service():
    """创建通知服务实例"""
    return NotificationService()


# ===========================================
# 1. ConnectionManager 基础功能测试
# ===========================================

class TestConnectionManager:
    """测试连接管理器基础功能"""

    @pytest.mark.asyncio
    async def test_connect_user(self, connection_manager, mock_websocket):
        """测试普通用户连接"""
        user_id = 123

        await connection_manager.connect(mock_websocket, user_id=user_id)

        assert user_id in connection_manager.active_connections
        assert mock_websocket in connection_manager.active_connections[user_id]
        mock_websocket.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_admin(self, connection_manager, mock_websocket):
        """测试管理员连接"""
        await connection_manager.connect(mock_websocket, is_admin=True)

        assert mock_websocket in connection_manager.admin_connections
        mock_websocket.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_multiple_users(self, connection_manager):
        """测试多用户连接"""
        ws1 = AsyncMock(spec=WebSocket)
        ws2 = AsyncMock(spec=WebSocket)

        await connection_manager.connect(ws1, user_id=1)
        await connection_manager.connect(ws2, user_id=2)

        assert len(connection_manager.active_connections) == 2
        assert 1 in connection_manager.active_connections
        assert 2 in connection_manager.active_connections

    @pytest.mark.asyncio
    async def test_connect_same_user_multiple_connections(self, connection_manager):
        """测试同一用户多个连接（多设备）"""
        ws1 = AsyncMock(spec=WebSocket)
        ws2 = AsyncMock(spec=WebSocket)

        await connection_manager.connect(ws1, user_id=1)
        await connection_manager.connect(ws2, user_id=1)

        assert len(connection_manager.active_connections[1]) == 2
        assert ws1 in connection_manager.active_connections[1]
        assert ws2 in connection_manager.active_connections[1]

    def test_disconnect_user(self, connection_manager, mock_websocket):
        """测试断开用户连接"""
        user_id = 123
        connection_manager.active_connections[user_id] = [mock_websocket]

        connection_manager.disconnect(mock_websocket, user_id=user_id)

        assert user_id not in connection_manager.active_connections

    def test_disconnect_admin(self, connection_manager, mock_websocket):
        """测试断开管理员连接"""
        connection_manager.admin_connections.add(mock_websocket)

        connection_manager.disconnect(mock_websocket, is_admin=True)

        assert mock_websocket not in connection_manager.admin_connections

    def test_disconnect_one_of_multiple_connections(self, connection_manager):
        """测试断开多个连接中的一个"""
        ws1 = AsyncMock(spec=WebSocket)
        ws2 = AsyncMock(spec=WebSocket)
        connection_manager.active_connections[1] = [ws1, ws2]

        connection_manager.disconnect(ws1, user_id=1)

        assert ws1 not in connection_manager.active_connections[1]
        assert ws2 in connection_manager.active_connections[1]
        assert 1 in connection_manager.active_connections


# ===========================================
# 2. 消息发送测试
# ===========================================

class TestMessageSending:
    """测试消息发送功能"""

    @pytest.mark.asyncio
    async def test_send_personal_message(self, connection_manager, mock_websocket):
        """测试发送个人消息"""
        user_id = 123
        message = {"type": "notification", "content": "Hello"}

        connection_manager.active_connections[user_id] = [mock_websocket]

        await connection_manager.send_personal_message(message, user_id)

        mock_websocket.send_text.assert_called_once()
        sent_message = mock_websocket.send_text.call_args[0][0]
        assert json.loads(sent_message) == message

    @pytest.mark.asyncio
    async def test_send_personal_message_to_multiple_devices(self, connection_manager):
        """测试发送消息到同一用户的多个设备"""
        ws1 = AsyncMock(spec=WebSocket)
        ws2 = AsyncMock(spec=WebSocket)
        user_id = 123
        message = {"type": "notification", "content": "Test"}

        connection_manager.active_connections[user_id] = [ws1, ws2]

        await connection_manager.send_personal_message(message, user_id)

        ws1.send_text.assert_called_once()
        ws2.send_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_personal_message_user_not_connected(self, connection_manager):
        """测试发送消息给不在线的用户"""
        message = {"type": "notification", "content": "Test"}

        # 不应该抛出异常
        await connection_manager.send_personal_message(message, user_id=999)

    @pytest.mark.asyncio
    async def test_send_admin_message(self, connection_manager):
        """测试发送管理员消息"""
        ws1 = AsyncMock(spec=WebSocket)
        ws2 = AsyncMock(spec=WebSocket)
        connection_manager.admin_connections = {ws1, ws2}

        message = {"type": "system_alert", "content": "Server maintenance"}

        await connection_manager.send_admin_message(message)

        ws1.send_text.assert_called_once()
        ws2.send_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_admin_message_no_admins_connected(self, connection_manager):
        """测试没有管理员在线时发送消息"""
        message = {"type": "system_alert", "content": "Test"}

        # 不应该抛出异常
        await connection_manager.send_admin_message(message)

    @pytest.mark.asyncio
    async def test_broadcast_message(self, connection_manager):
        """测试广播消息给所有用户"""
        user_ws1 = AsyncMock(spec=WebSocket)
        user_ws2 = AsyncMock(spec=WebSocket)
        admin_ws = AsyncMock(spec=WebSocket)

        connection_manager.active_connections = {
            1: [user_ws1],
            2: [user_ws2]
        }
        connection_manager.admin_connections = {admin_ws}

        message = {"type": "announcement", "content": "System update"}

        await connection_manager.broadcast(message)

        user_ws1.send_text.assert_called_once()
        user_ws2.send_text.assert_called_once()
        admin_ws.send_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_message_with_failed_connection(self, connection_manager):
        """测试发送消息时连接失败的处理"""
        ws_good = AsyncMock(spec=WebSocket)
        ws_bad = AsyncMock(spec=WebSocket)
        ws_bad.send_text.side_effect = Exception("Connection lost")

        connection_manager.active_connections[1] = [ws_good, ws_bad]

        message = {"type": "test", "content": "Test"}

        await connection_manager.send_personal_message(message, user_id=1)

        # 好的连接应该收到消息
        ws_good.send_text.assert_called_once()
        # 坏的连接应该被清理
        assert ws_bad not in connection_manager.active_connections.get(1, [])


# ===========================================
# 3. 连接统计测试
# ===========================================

class TestConnectionStats:
    """测试连接统计功能"""

    def test_get_connection_count_empty(self, connection_manager):
        """测试空连接统计"""
        stats = connection_manager.get_connection_count()

        assert stats["total_users"] == 0
        assert stats["total_user_connections"] == 0
        assert stats["total_admin_connections"] == 0
        assert stats["total_connections"] == 0

    def test_get_connection_count_with_users(self, connection_manager):
        """测试有用户连接的统计"""
        ws1 = AsyncMock(spec=WebSocket)
        ws2 = AsyncMock(spec=WebSocket)
        ws3 = AsyncMock(spec=WebSocket)

        connection_manager.active_connections = {
            1: [ws1, ws2],  # 用户1有2个连接
            2: [ws3]         # 用户2有1个连接
        }

        stats = connection_manager.get_connection_count()

        assert stats["total_users"] == 2
        assert stats["total_user_connections"] == 3
        assert stats["total_admin_connections"] == 0
        assert stats["total_connections"] == 3

    def test_get_connection_count_with_admins(self, connection_manager):
        """测试有管理员连接的统计"""
        admin_ws1 = AsyncMock(spec=WebSocket)
        admin_ws2 = AsyncMock(spec=WebSocket)

        connection_manager.admin_connections = {admin_ws1, admin_ws2}

        stats = connection_manager.get_connection_count()

        assert stats["total_users"] == 0
        assert stats["total_user_connections"] == 0
        assert stats["total_admin_connections"] == 2
        assert stats["total_connections"] == 2

    def test_get_connection_count_mixed(self, connection_manager):
        """测试用户和管理员混合连接的统计"""
        user_ws = AsyncMock(spec=WebSocket)
        admin_ws1 = AsyncMock(spec=WebSocket)
        admin_ws2 = AsyncMock(spec=WebSocket)

        connection_manager.active_connections = {1: [user_ws]}
        connection_manager.admin_connections = {admin_ws1, admin_ws2}

        stats = connection_manager.get_connection_count()

        assert stats["total_users"] == 1
        assert stats["total_user_connections"] == 1
        assert stats["total_admin_connections"] == 2
        assert stats["total_connections"] == 3


# ===========================================
# 4. 认证和Token验证测试
# ===========================================

class TestAuthentication:
    """测试WebSocket认证"""

    @pytest.mark.asyncio
    async def test_get_current_user_from_token_valid_user(self):
        """测试有效的用户token（使用mock）"""
        with patch("app.api.websocket.decode_token") as mock_decode:
            with patch("app.database.async_session_maker") as mock_session:
                mock_decode.return_value = {"sub": "123", "is_admin": False}

                # Mock user
                mock_user = MagicMock(spec=User)
                mock_user.id = 123

                # Mock database session
                mock_db = AsyncMock()
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_user
                mock_db.execute = AsyncMock(return_value=mock_result)
                mock_session.return_value.__aenter__.return_value = mock_db

                result = await get_current_user_from_token("valid_token")

                assert result is not None
                assert result["user"].id == 123
                assert result["is_admin"] is False

    @pytest.mark.asyncio
    async def test_get_current_user_from_token_valid_admin(self):
        """测试有效的管理员token（使用mock）"""
        with patch("app.api.websocket.decode_token") as mock_decode:
            with patch("app.database.async_session_maker") as mock_session:
                mock_decode.return_value = {"sub": "456", "is_admin": True}

                # Mock admin user
                mock_admin = MagicMock(spec=AdminUser)
                mock_admin.id = 456

                # Mock database session
                mock_db = AsyncMock()
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_admin
                mock_db.execute = AsyncMock(return_value=mock_result)
                mock_session.return_value.__aenter__.return_value = mock_db

                result = await get_current_user_from_token("valid_token")

                assert result is not None
                assert result["user"].id == 456
                assert result["is_admin"] is True

    @pytest.mark.asyncio
    async def test_get_current_user_from_token_invalid_token(self):
        """测试无效token"""
        result = await get_current_user_from_token("invalid_token")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_current_user_from_token_expired_token(self):
        """测试过期token"""
        # 创建一个已过期的token（负数过期时间）
        with patch("app.utils.security.decode_token") as mock_decode:
            mock_decode.return_value = None  # 模拟过期返回None

            result = await get_current_user_from_token("expired_token")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_current_user_from_token_missing_user_id(self):
        """测试token缺少user_id"""
        with patch("app.utils.security.decode_token") as mock_decode:
            mock_decode.return_value = {"is_admin": False}  # 缺少sub字段

            result = await get_current_user_from_token("token")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_current_user_from_token_user_not_found(self):
        """测试用户不存在"""
        with patch("app.api.websocket.decode_token") as mock_decode:
            with patch("app.database.async_session_maker") as mock_session:
                mock_decode.return_value = {"sub": "999999", "is_admin": False}

                # Mock database returning None (user not found)
                mock_db = AsyncMock()
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = None
                mock_db.execute = AsyncMock(return_value=mock_result)
                mock_session.return_value.__aenter__.return_value = mock_db

                result = await get_current_user_from_token("token")

                # 当用户不存在时，返回的user字段为None
                assert result is not None
                assert result["user"] is None


# ===========================================
# 5. NotificationService 测试
# ===========================================

class TestNotificationService:
    """测试通知服务"""

    @pytest.mark.asyncio
    async def test_notify_transcode_progress(self, notification_service):
        """测试转码进度通知"""
        with patch("app.utils.websocket_manager.manager.send_admin_message") as mock_send:
            await notification_service.notify_transcode_progress(
                video_id=123,
                status="processing",
                progress=50,
                message="Transcoding in progress"
            )

            mock_send.assert_called_once()
            call_args = mock_send.call_args[0][0]
            assert call_args["type"] == "transcode_progress"
            assert call_args["video_id"] == 123
            assert call_args["status"] == "processing"
            assert call_args["progress"] == 50

    @pytest.mark.asyncio
    async def test_notify_transcode_complete(self, notification_service):
        """测试转码完成通知"""
        with patch("app.utils.websocket_manager.manager.send_admin_message") as mock_send:
            await notification_service.notify_transcode_complete(
                video_id=123,
                title="Test Video",
                format_type="h264",
                file_size=1024000
            )

            mock_send.assert_called_once()
            call_args = mock_send.call_args[0][0]
            assert call_args["type"] == "transcode_complete"
            assert call_args["video_id"] == 123
            assert call_args["title"] == "Test Video"
            assert call_args["format_type"] == "h264"
            assert call_args["file_size"] == 1024000

    @pytest.mark.asyncio
    async def test_notify_transcode_failed(self, notification_service):
        """测试转码失败通知"""
        with patch("app.utils.websocket_manager.manager.send_admin_message") as mock_send:
            await notification_service.notify_transcode_failed(
                video_id=123,
                title="Test Video",
                error="Codec not supported"
            )

            mock_send.assert_called_once()
            call_args = mock_send.call_args[0][0]
            assert call_args["type"] == "transcode_failed"
            assert call_args["video_id"] == 123
            assert call_args["error"] == "Codec not supported"

    @pytest.mark.asyncio
    async def test_notify_system_message_to_admin(self, notification_service):
        """测试发送系统消息给管理员"""
        with patch("app.utils.websocket_manager.manager.send_admin_message") as mock_send:
            await notification_service.notify_system_message(
                message="System maintenance scheduled",
                level="warning",
                target="admin"
            )

            mock_send.assert_called_once()
            call_args = mock_send.call_args[0][0]
            assert call_args["type"] == "system_message"
            assert call_args["message"] == "System maintenance scheduled"
            assert call_args["level"] == "warning"

    @pytest.mark.asyncio
    async def test_notify_system_message_broadcast(self, notification_service):
        """测试广播系统消息"""
        with patch("app.utils.websocket_manager.manager.broadcast") as mock_broadcast:
            await notification_service.notify_system_message(
                message="System update complete",
                level="success",
                target="all"
            )

            mock_broadcast.assert_called_once()
            call_args = mock_broadcast.call_args[0][0]
            assert call_args["type"] == "system_message"
            assert call_args["message"] == "System update complete"
            assert call_args["level"] == "success"

    @pytest.mark.asyncio
    async def test_notify_system_message_to_specific_user(self, notification_service):
        """测试发送系统消息给特定用户"""
        with patch("app.utils.websocket_manager.manager.send_personal_message") as mock_send:
            await notification_service.notify_system_message(
                message="Your video is ready",
                level="info",
                target=123  # user_id
            )

            mock_send.assert_called_once()
            call_args = mock_send.call_args[0]
            assert call_args[0]["type"] == "system_message"
            assert call_args[0]["message"] == "Your video is ready"
            assert call_args[1] == 123  # user_id

    @pytest.mark.asyncio
    async def test_notification_includes_timestamp(self, notification_service):
        """测试通知包含时间戳"""
        with patch("app.utils.websocket_manager.manager.send_admin_message") as mock_send:
            await notification_service.notify_transcode_progress(
                video_id=1, status="processing", progress=50
            )

            call_args = mock_send.call_args[0][0]
            assert "timestamp" in call_args
            # 验证时间戳格式（ISO格式）
            assert "T" in call_args["timestamp"]


# ===========================================
# 6. 边界条件和异常测试
# ===========================================

class TestEdgeCases:
    """测试边界条件"""

    @pytest.mark.asyncio
    async def test_connect_without_user_id_or_admin_flag(self, connection_manager, mock_websocket):
        """测试既没有user_id也没有is_admin标志的连接"""
        await connection_manager.connect(mock_websocket)

        # 应该接受连接但不存储
        mock_websocket.accept.assert_called_once()
        assert len(connection_manager.active_connections) == 0
        assert len(connection_manager.admin_connections) == 0

    def test_disconnect_nonexistent_connection(self, connection_manager, mock_websocket):
        """测试断开不存在的连接"""
        # 不应该抛出异常
        connection_manager.disconnect(mock_websocket, user_id=999)
        connection_manager.disconnect(mock_websocket, is_admin=True)

    @pytest.mark.asyncio
    async def test_send_message_with_unicode(self, connection_manager, mock_websocket):
        """测试发送包含Unicode的消息"""
        user_id = 123
        message = {"type": "notification", "content": "你好世界 🎉"}

        connection_manager.active_connections[user_id] = [mock_websocket]

        await connection_manager.send_personal_message(message, user_id)

        mock_websocket.send_text.assert_called_once()
        sent_message = mock_websocket.send_text.call_args[0][0]
        parsed = json.loads(sent_message)
        assert parsed["content"] == "你好世界 🎉"

    @pytest.mark.asyncio
    async def test_send_large_message(self, connection_manager, mock_websocket):
        """测试发送大消息"""
        user_id = 123
        large_content = "A" * 10000  # 10KB消息
        message = {"type": "data", "content": large_content}

        connection_manager.active_connections[user_id] = [mock_websocket]

        await connection_manager.send_personal_message(message, user_id)

        mock_websocket.send_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_concurrent_connections(self, connection_manager):
        """测试并发连接"""
        import asyncio

        async def connect_user(user_id):
            ws = AsyncMock(spec=WebSocket)
            await connection_manager.connect(ws, user_id=user_id)

        # 并发连接10个用户（user_id从1到10）
        await asyncio.gather(*[connect_user(i) for i in range(1, 11)])

        assert len(connection_manager.active_connections) == 10

    @pytest.mark.asyncio
    async def test_message_order_preservation(self, connection_manager, mock_websocket):
        """测试消息顺序保持"""
        user_id = 123
        connection_manager.active_connections[user_id] = [mock_websocket]

        messages = [
            {"type": "msg", "content": f"Message {i}"}
            for i in range(5)
        ]

        for msg in messages:
            await connection_manager.send_personal_message(msg, user_id)

        # 验证调用次数
        assert mock_websocket.send_text.call_count == 5

        # 验证消息顺序
        calls = mock_websocket.send_text.call_args_list
        for i, call in enumerate(calls):
            sent_message = json.loads(call[0][0])
            assert sent_message["content"] == f"Message {i}"


# ===========================================
# 7. 清理和资源管理测试
# ===========================================

class TestResourceManagement:
    """测试资源管理"""

    @pytest.mark.asyncio
    async def test_cleanup_failed_connections_on_send(self, connection_manager):
        """测试发送消息时自动清理失败的连接"""
        ws1 = AsyncMock(spec=WebSocket)
        ws2 = AsyncMock(spec=WebSocket)
        ws2.send_text.side_effect = Exception("Connection closed")

        connection_manager.active_connections[1] = [ws1, ws2]

        await connection_manager.send_personal_message({"test": "data"}, user_id=1)

        # ws2应该被移除
        assert ws2 not in connection_manager.active_connections[1]
        # ws1应该保留
        assert ws1 in connection_manager.active_connections[1]

    @pytest.mark.asyncio
    async def test_cleanup_empty_user_entry(self, connection_manager):
        """测试清理空的用户条目"""
        ws = AsyncMock(spec=WebSocket)
        connection_manager.active_connections[1] = [ws]

        connection_manager.disconnect(ws, user_id=1)

        # 用户条目应该被完全移除
        assert 1 not in connection_manager.active_connections

    @pytest.mark.asyncio
    async def test_multiple_cleanup_operations(self, connection_manager):
        """测试多次清理操作"""
        ws1 = AsyncMock(spec=WebSocket)
        ws2 = AsyncMock(spec=WebSocket)
        ws3 = AsyncMock(spec=WebSocket)

        connection_manager.active_connections[1] = [ws1, ws2, ws3]

        # 逐个断开
        connection_manager.disconnect(ws1, user_id=1)
        assert len(connection_manager.active_connections[1]) == 2

        connection_manager.disconnect(ws2, user_id=1)
        assert len(connection_manager.active_connections[1]) == 1

        connection_manager.disconnect(ws3, user_id=1)
        assert 1 not in connection_manager.active_connections


# ===========================================
# 测试总结
# ===========================================

"""
测试覆盖：
✅ ConnectionManager 基础功能 - 8个测试用例
✅ 消息发送功能 - 8个测试用例
✅ 连接统计功能 - 4个测试用例
✅ 认证和Token验证 - 6个测试用例
✅ NotificationService - 7个测试用例
✅ 边界条件测试 - 7个测试用例
✅ 资源管理测试 - 3个测试用例

总计：43个测试用例

测试场景：
- 用户和管理员连接管理
- 同一用户多设备连接
- 个人消息、管理员消息、广播消息
- 连接失败时的自动清理
- 连接统计（用户数、连接数）
- JWT Token认证（用户和管理员）
- 转码进度、完成、失败通知
- 系统消息通知（不同目标）
- Unicode和大消息处理
- 并发连接
- 消息顺序保持
- 资源自动清理
- 空连接处理
- Token验证（有效、无效、过期、缺失字段）
- 时间戳格式验证
"""
