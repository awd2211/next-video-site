"""
测试管理员通知系统
包括API调用和WebSocket集成
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from app.utils.admin_notification_service import AdminNotificationService
from app.models.notification import NotificationType


async def test_admin_notifications():
    """测试管理员通知系统"""

    print("=" * 60)
    print("测试管理员通知系统")
    print("=" * 60)

    db: AsyncSession = SessionLocal()

    try:
        # 1. 创建测试通知
        print("\n1. 创建测试通知...")
        notification = await AdminNotificationService.create_admin_notification(
            db=db,
            admin_user_id=None,  # 广播给所有管理员
            type=NotificationType.SYSTEM_ERROR_ALERT,
            title="系统错误测试",
            content="这是一条测试系统错误通知，用于验证通知系统是否正常工作。",
            severity="error",
            link="/logs?tab=error",
            send_websocket=True,  # 发送WebSocket通知
        )
        print(f"✅ 通知已创建: ID={notification.id}")

        # 2. 获取未读通知数量
        print("\n2. 获取未读通知数量...")
        unread_count = await AdminNotificationService.get_unread_count(db)
        print(f"✅ 未读通知数量: {unread_count}")

        # 3. 创建不同严重程度的通知
        print("\n3. 创建不同严重程度的通知...")

        severities = [
            ("info", "信息通知", "这是一条信息通知"),
            ("warning", "警告通知", "这是一条警告通知"),
            ("error", "错误通知", "这是一条错误通知"),
            ("critical", "严重错误通知", "这是一条严重错误通知"),
        ]

        for severity, title, content in severities:
            await AdminNotificationService.create_admin_notification(
                db=db,
                admin_user_id=None,
                type="test_notification",
                title=title,
                content=content,
                severity=severity,
                send_websocket=True,
            )
            print(f"  ✅ 创建 {severity} 级别通知: {title}")

        # 4. 测试特定通知类型
        print("\n4. 测试特定通知类型...")

        # 新用户注册通知
        await AdminNotificationService.notify_new_user_registration(
            db=db,
            user_id=99999,
            username="test_user",
            email="test@example.com",
        )
        print("  ✅ 新用户注册通知已创建")

        # 存储空间警告
        await AdminNotificationService.notify_storage_warning(
            db=db,
            usage_percent=85.5,
            used_gb=85.5,
            total_gb=100.0,
        )
        print("  ✅ 存储空间警告通知已创建")

        # 系统错误告警
        await AdminNotificationService.notify_system_error(
            db=db,
            error_type="DatabaseError",
            error_message="连接数据库失败",
            error_id=1,
        )
        print("  ✅ 系统错误告警通知已创建")

        # 5. 再次获取未读通知数量
        print("\n5. 再次获取未读通知数量...")
        unread_count = await AdminNotificationService.get_unread_count(db)
        print(f"✅ 未读通知数量: {unread_count}")

        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        print("\n提示:")
        print("1. 打开管理后台查看通知徽章是否有红点")
        print("2. 点击通知图标查看通知列表")
        print("3. 如果WebSocket已连接,应该会收到实时通知弹窗")
        print("4. 访问 http://localhost:8000/api/v1/admin/notifications 查看通知API")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(test_admin_notifications())
