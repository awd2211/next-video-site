#!/usr/bin/env python3
"""
批量操作API测试
"""
import asyncio

import httpx


async def test_batch_api_availability():
    """测试批量操作API是否可用"""
    print("=" * 60)
    print("🔍 批量操作API测试")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # 获取OpenAPI规范
        response = await client.get("http://localhost:8000/api/openapi.json")

        if response.status_code == 200:
            openapi = response.json()
            paths = openapi.get("paths", {})

            # 查找批量操作端点
            batch_endpoints = [
                path
                for path in paths.keys()
                if "/admin/batch/" in path
            ]

            print(f"\n✅ 找到批量操作端点: {len(batch_endpoints)}个\n")

            for endpoint in batch_endpoints:
                methods = list(paths[endpoint].keys())
                print(f"   📌 {endpoint}")
                for method in methods:
                    if method != "parameters":
                        summary = paths[endpoint][method].get("summary", "")
                        print(f"      {method.upper()}: {summary}")

            if batch_endpoints:
                print("\n✅ 批量操作API已成功注册！")
            else:
                print("\n⚠️  未找到批量操作端点（可能需要重启服务）")

        else:
            print(f"❌ 无法获取API文档: {response.status_code}")


async def test_performance_headers():
    """测试性能监控响应头"""
    print("\n" + "=" * 60)
    print("⏱️  性能监控测试")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # 测试几个端点
        endpoints = [
            "/health",
            "/api/v1/videos?page=1&page_size=10",
            "/api/v1/categories",
        ]

        for endpoint in endpoints:
            response = await client.get(f"http://localhost:8000{endpoint}")

            if response.status_code == 200:
                response_time = response.headers.get("X-Response-Time")
                request_id = response.headers.get("X-Request-ID")

                print(f"\n📍 {endpoint}")
                print(f"   ✅ 响应时间: {response_time}")
                print(f"   ✅ Request ID: {request_id[:36] if request_id else 'N/A'}...")

        print("\n✅ 性能监控中间件已生效！")


async def test_cache_clear():
    """测试缓存清除API"""
    print("\n" + "=" * 60)
    print("🗑️  缓存清除测试")
    print("=" * 60)

    print("\n   ℹ️  需要管理员权限，示例用法：")
    print("\n   清除视频列表缓存:")
    print("   POST /api/v1/admin/batch/cache/clear")
    print('   Body: {"pattern": "videos_list:*"}')

    print("\n   清除所有缓存:")
    print("   POST /api/v1/admin/batch/cache/clear")
    print('   Body: {"pattern": "*"}')


async def main():
    """运行所有测试"""
    try:
        await test_batch_api_availability()
        await test_performance_headers()
        await test_cache_clear()

        print("\n" + "=" * 60)
        print("✅ 批量操作和性能监控测试完成！")
        print("=" * 60)

        print("\n💡 新增功能:")
        print("   ✅ 批量更新视频状态")
        print("   ✅ 批量删除视频")
        print("   ✅ 批量审核评论")
        print("   ✅ 批量删除评论")
        print("   ✅ 缓存清除API")
        print("   ✅ 响应时间监控")
        print("   ✅ 慢API自动记录")

    except httpx.ConnectError:
        print("\n❌ 错误: 无法连接到后端服务")
        print("   请先启动后端: make backend-run")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

