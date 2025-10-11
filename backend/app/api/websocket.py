"""
WebSocket API端点
提供实时通知功能
"""

import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.database import SessionLocal
from app.models.user import AdminUser, User
from app.utils.security import decode_token
from app.utils.websocket_manager import manager

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_current_user_from_token(token: str):
    """从token获取当前用户"""
    try:
        payload = decode_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        is_admin = payload.get("is_admin", False)

        db = SessionLocal()
        try:
            if is_admin:
                result = await db.execute(
                    select(AdminUser).where(AdminUser.id == int(user_id))
                )
                user = result.scalar_one_or_none()
            else:
                result = await db.execute(select(User).where(User.id == int(user_id)))
                user = result.scalar_one_or_none()

            return {"user": user, "is_admin": is_admin}
        finally:
            await db.close()
    except Exception as e:
        logger.error(f"Token验证失败: {str(e)}")
        return None


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT访问令牌（必需）"),  # 强制要求token
):
    """
    WebSocket端点 (普通用户)

    连接URL: ws://localhost:8000/api/v1/ws?token=<access_token>

    注意：token参数是必需的，未认证的连接将被拒绝

    消息格式:
    - type: 消息类型 (ping/subscribe/unsubscribe)
    - data: 消息数据
    """
    # 验证token
    auth_result = await get_current_user_from_token(token)
    if not auth_result or not auth_result["user"]:
        await websocket.close(code=1008, reason="无效的访问令牌")
        return

    user = auth_result["user"]
    user_id = user.id

    # 建立连接
    await manager.connect(websocket, user_id=user_id)

    try:
        # 发送连接成功消息
        await websocket.send_json(
            {
                "type": "connected",
                "message": f"欢迎, {user.username}!",
                "user_id": user_id,
            }
        )

        # 保持连接,监听客户端消息
        while True:
            data = await websocket.receive_text()

            # 处理心跳
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id=user_id)
        logger.info(f"用户 {user_id} WebSocket连接断开")
    except Exception as e:
        logger.error(f"WebSocket错误: {str(e)}")
        manager.disconnect(websocket, user_id=user_id)


@router.websocket("/ws/admin")
async def admin_websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT访问令牌（必需）"),  # 强制要求token
):
    """
    WebSocket端点 (管理员)

    连接URL: ws://localhost:8000/api/v1/ws/admin?token=<access_token>

    注意：token参数是必需的，未认证的连接将被拒绝

    接收消息类型:
    - transcode_progress: 转码进度更新
    - transcode_complete: 转码完成
    - transcode_failed: 转码失败
    - system_message: 系统消息
    """
    if not token:
        await websocket.close(code=1008, reason="缺少访问令牌")
        return

    # 验证token
    auth_result = await get_current_user_from_token(token)
    if not auth_result or not auth_result["user"] or not auth_result["is_admin"]:
        await websocket.close(code=1008, reason="需要管理员权限")
        return

    admin_user = auth_result["user"]

    # 建立连接
    await manager.connect(websocket, is_admin=True)

    try:
        # 发送连接成功消息
        await websocket.send_json(
            {
                "type": "connected",
                "message": f"管理员 {admin_user.username} 已连接",
                "admin_id": admin_user.id,
                "connection_stats": manager.get_connection_count(),
            }
        )

        # 保持连接,监听客户端消息
        while True:
            data = await websocket.receive_text()

            # 处理心跳
            if data == "ping":
                await websocket.send_text("pong")
            # 管理员可以请求连接统计
            elif data == "get_stats":
                await websocket.send_json(
                    {"type": "connection_stats", "data": manager.get_connection_count()}
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, is_admin=True)
        logger.info(f"管理员 {admin_user.id} WebSocket连接断开")
    except Exception as e:
        logger.error(f"管理员WebSocket错误: {str(e)}")
        manager.disconnect(websocket, is_admin=True)


@router.get("/ws/stats")
async def get_websocket_stats():
    """
    获取WebSocket连接统计 (用于调试)

    Returns:
        {
            "total_users": 10,
            "total_user_connections": 15,
            "total_admin_connections": 3,
            "total_connections": 18
        }
    """
    return manager.get_connection_count()
