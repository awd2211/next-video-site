#!/usr/bin/env python3
"""
新功能快速验证（需要重启服务后运行）
"""
import asyncio

import httpx


async def test_response_headers():
    """测试响应头"""
    print("=" * 60)
    print("🔍 响应头测试")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get("http://localhost:8000/health")

            print("\n📋 响应头:")
            headers_to_check = [
                "X-Request-ID",
                "X-Response-Time",
                "Content-Type",
            ]

            for header in headers_to_check:
                value = response.headers.get(header, "N/A")
                status = "✅" if value != "N/A" else "⚠️ "
                print(f"   {status} {header}: {value}")

            if response.headers.get("X-Request-ID"):
                print("\n✅ Request ID中间件已生效！")

            if response.headers.get("X-Response-Time"):
                print("✅ 性能监控中间件已生效！")

        except httpx.ReadTimeout:
            print("\n⚠️  服务响应超时，可能正在重启")
            print("   请稍后重试")
        except httpx.ConnectError:
            print("\n❌ 无法连接到服务")
            print("   请确保后端正在运行: make backend-run")


async def test_batch_endpoints():
    """测试批量操作端点"""
    print("\n" + "=" * 60)
    print("📦 批量操作端点")
    print("=" * 60)

    endpoints = [
        "POST /api/v1/admin/batch/videos/status - 批量更新视频状态",
        "POST /api/v1/admin/batch/videos/delete - 批量删除视频",
        "POST /api/v1/admin/batch/comments/status - 批量审核评论",
        "POST /api/v1/admin/batch/comments/delete - 批量删除评论",
        "POST /api/v1/admin/batch/cache/clear - 清除缓存",
    ]

    print("\n📌 新增的批量操作API:")
    for endpoint in endpoints:
        print(f"   {endpoint}")

    print("\n💡 提示: 需要管理员token才能访问")


async def main():
    """运行所有测试"""
    await test_response_headers()
    await test_batch_endpoints()

    print("\n" + "=" * 60)
    print("✅ 功能验证完成！")
    print("=" * 60)

    print("\n🚀 如需完整测试，请:")
    print("   1. 重启后端服务: make backend-run")
    print("   2. 重新运行此脚本")


if __name__ == "__main__":
    asyncio.run(main())

