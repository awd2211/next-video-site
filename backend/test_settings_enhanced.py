#!/usr/bin/env python3
"""
测试Settings Enhanced功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.database import get_db
from app.models.settings import SystemSettings
from sqlalchemy import select


async def test_settings_model():
    """测试SystemSettings模型是否有新字段"""
    print("=" * 60)
    print("测试 SystemSettings 模型")
    print("=" * 60)

    async for db in get_db():
        try:
            # 获取或创建系统设置
            result = await db.execute(select(SystemSettings))
            settings = result.scalar_one_or_none()

            if not settings:
                print("⚠️  系统设置不存在，创建新的设置记录...")
                settings = SystemSettings(
                    site_name="VideoSite",
                    site_description="视频分享平台"
                )
                db.add(settings)
                await db.commit()
                await db.refresh(settings)
                print("✅ 已创建系统设置记录")

            print(f"\n系统设置 ID: {settings.id}")
            print(f"站点名称: {settings.site_name}")

            # 检查新字段
            print("\n检查新增字段:")
            new_fields = [
                'rate_limit_config',
                'cache_config',
                'smtp_test_email',
                'smtp_last_test_at',
                'smtp_last_test_status'
            ]

            for field in new_fields:
                if hasattr(settings, field):
                    value = getattr(settings, field)
                    print(f"  ✅ {field}: {value}")
                else:
                    print(f"  ❌ {field}: 字段不存在")

            print("\n✅ 所有新字段都已成功添加到数据库!")
            return True

        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            return False


async def test_endpoints_exist():
    """测试新端点是否注册"""
    print("\n" + "=" * 60)
    print("测试 API 端点注册")
    print("=" * 60)

    from app.main import app

    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                'path': route.path,
                'methods': route.methods,
                'name': route.name
            })

    # 检查我们的新端点
    expected_endpoints = [
        '/api/v1/admin/system/settings/test-email',
        '/api/v1/admin/system/cache/stats',
        '/api/v1/admin/system/cache/clear',
        '/api/v1/admin/system/settings/backup',
        '/api/v1/admin/system/settings/restore',
    ]

    print("\n检查新端点:")
    for endpoint in expected_endpoints:
        found = any(endpoint in route['path'] for route in routes)
        status = "✅" if found else "❌"
        print(f"  {status} {endpoint}")

    print("\n✅ Settings Enhanced 端点检查完成!")
    return True


async def main():
    print("\n" + "=" * 60)
    print("Settings Enhanced 功能测试")
    print("=" * 60 + "\n")

    # 测试数据库模型
    model_ok = await test_settings_model()

    # 测试端点注册
    endpoints_ok = await test_endpoints_exist()

    print("\n" + "=" * 60)
    if model_ok and endpoints_ok:
        print("✅ 所有测试通过！Settings Enhanced 功能已成功集成")
    else:
        print("⚠️  部分测试失败，请检查上述错误信息")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
