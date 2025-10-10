"""
WebSocket连接管理器
用于实时通知推送 (转码进度、系统消息等)
"""
from typing import Dict, List, Set
from fastapi import WebSocket
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 存储所有活跃连接 {user_id: [websocket1, websocket2...]}
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # 管理员连接 (不区分user_id)
        self.admin_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, user_id: int = None, is_admin: bool = False):
        """
        建立WebSocket连接

        Args:
            websocket: WebSocket连接对象
            user_id: 用户ID (普通用户)
            is_admin: 是否为管理员
        """
        await websocket.accept()

        if is_admin:
            self.admin_connections.add(websocket)
            logger.info(f"✅ Admin WebSocket连接已建立, 当前管理员连接数: {len(self.admin_connections)}")
        elif user_id:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)
            logger.info(f"✅ User {user_id} WebSocket连接已建立, 该用户连接数: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: int = None, is_admin: bool = False):
        """
        断开WebSocket连接

        Args:
            websocket: WebSocket连接对象
            user_id: 用户ID
            is_admin: 是否为管理员
        """
        if is_admin and websocket in self.admin_connections:
            self.admin_connections.remove(websocket)
            logger.info(f"❌ Admin WebSocket连接已断开, 剩余管理员连接数: {len(self.admin_connections)}")
        elif user_id and user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
                # 如果该用户没有连接了,删除键
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
                logger.info(f"❌ User {user_id} WebSocket连接已断开")

    async def send_personal_message(self, message: dict, user_id: int):
        """
        发送消息给指定用户的所有连接

        Args:
            message: 消息内容
            user_id: 用户ID
        """
        if user_id not in self.active_connections:
            logger.warning(f"用户 {user_id} 没有活跃的WebSocket连接")
            return

        message_text = json.dumps(message, ensure_ascii=False)

        # 发送给该用户的所有连接
        disconnected = []
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_text(message_text)
            except Exception as e:
                logger.error(f"发送消息给用户 {user_id} 失败: {str(e)}")
                disconnected.append(websocket)

        # 清理失败的连接
        for ws in disconnected:
            self.disconnect(ws, user_id)

    async def send_admin_message(self, message: dict):
        """
        发送消息给所有管理员

        Args:
            message: 消息内容
        """
        if not self.admin_connections:
            logger.warning("没有活跃的管理员WebSocket连接")
            return

        message_text = json.dumps(message, ensure_ascii=False)

        disconnected = []
        for websocket in self.admin_connections:
            try:
                await websocket.send_text(message_text)
            except Exception as e:
                logger.error(f"发送管理员消息失败: {str(e)}")
                disconnected.append(websocket)

        # 清理失败的连接
        for ws in disconnected:
            self.disconnect(ws, is_admin=True)

    async def broadcast(self, message: dict):
        """
        广播消息给所有用户

        Args:
            message: 消息内容
        """
        message_text = json.dumps(message, ensure_ascii=False)

        # 给所有普通用户广播
        for user_id, connections in list(self.active_connections.items()):
            disconnected = []
            for websocket in connections:
                try:
                    await websocket.send_text(message_text)
                except Exception as e:
                    logger.error(f"广播消息给用户 {user_id} 失败: {str(e)}")
                    disconnected.append(websocket)

            for ws in disconnected:
                self.disconnect(ws, user_id)

        # 给所有管理员广播
        await self.send_admin_message(message)

    def get_connection_count(self) -> dict:
        """获取连接统计"""
        user_count = sum(len(conns) for conns in self.active_connections.values())
        return {
            "total_users": len(self.active_connections),
            "total_user_connections": user_count,
            "total_admin_connections": len(self.admin_connections),
            "total_connections": user_count + len(self.admin_connections)
        }


# 全局连接管理器实例
manager = ConnectionManager()


class NotificationService:
    """通知服务"""

    @staticmethod
    async def notify_transcode_progress(
        video_id: int,
        status: str,
        progress: int,
        message: str = None
    ):
        """
        通知转码进度更新

        Args:
            video_id: 视频ID
            status: 转码状态 (pending/processing/completed/failed)
            progress: 进度百分比 (0-100)
            message: 附加消息
        """
        notification = {
            "type": "transcode_progress",
            "video_id": video_id,
            "status": status,
            "progress": progress,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

        # 发送给所有管理员
        await manager.send_admin_message(notification)
        logger.info(f"📡 转码进度通知已发送: video_id={video_id}, status={status}, progress={progress}%")

    @staticmethod
    async def notify_transcode_complete(
        video_id: int,
        title: str,
        format_type: str,
        file_size: int
    ):
        """
        通知转码完成

        Args:
            video_id: 视频ID
            title: 视频标题
            format_type: 转码格式 (h264/av1)
            file_size: 文件大小
        """
        notification = {
            "type": "transcode_complete",
            "video_id": video_id,
            "title": title,
            "format_type": format_type,
            "file_size": file_size,
            "timestamp": datetime.now().isoformat()
        }

        await manager.send_admin_message(notification)
        logger.info(f"✅ 转码完成通知已发送: video_id={video_id}, format={format_type}")

    @staticmethod
    async def notify_transcode_failed(
        video_id: int,
        title: str,
        error: str
    ):
        """
        通知转码失败

        Args:
            video_id: 视频ID
            title: 视频标题
            error: 错误信息
        """
        notification = {
            "type": "transcode_failed",
            "video_id": video_id,
            "title": title,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }

        await manager.send_admin_message(notification)
        logger.error(f"❌ 转码失败通知已发送: video_id={video_id}, error={error}")

    @staticmethod
    async def notify_system_message(
        message: str,
        level: str = "info",
        target: str = "admin"
    ):
        """
        发送系统消息

        Args:
            message: 消息内容
            level: 消息级别 (info/warning/error/success)
            target: 目标 (admin/all/user_id)
        """
        notification = {
            "type": "system_message",
            "message": message,
            "level": level,
            "timestamp": datetime.now().isoformat()
        }

        if target == "admin":
            await manager.send_admin_message(notification)
        elif target == "all":
            await manager.broadcast(notification)
        elif isinstance(target, int):
            await manager.send_personal_message(notification, target)

        logger.info(f"📢 系统消息已发送: message={message}, level={level}, target={target}")


# 全局通知服务实例
notification_service = NotificationService()
