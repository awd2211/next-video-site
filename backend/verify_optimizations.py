#!/usr/bin/env python3
"""
验证后端优化效果
"""
import asyncio
import time

import httpx


async def test_video_detail_cache():
    """测试视频详情缓存效果"""
    print("\n1️⃣ 测试视频详情缓存...")

    async with httpx.AsyncClient() as client:
        # 先获取一个存在的视频ID
        list_response = await client.get("http://localhost:8000/api/v1/videos?page=1&page_size=1")
        if list_response.status_code != 200 or list_response.json()["total"] == 0:
            print("   ⚠️ 没有视频数据，跳过测试")
            return

        video_id = list_response.json()["items"][0]["id"]

        # 第一次请求（无缓存）
        start = time.time()
        response1 = await client.get(f"http://localhost:8000/api/v1/videos/{video_id}")
        time1 = time.time() - start

        # 第二次请求（有缓存）
        start = time.time()
        response2 = await client.get(f"http://localhost:8000/api/v1/videos/{video_id}")
        time2 = time.time() - start

        if response1.status_code == 200 and response2.status_code == 200:
            print(f"   ✅ 视频ID: {video_id}")
            print(f"   ✅ 第一次请求: {time1*1000:.0f}ms")
            print(f"   ✅ 第二次请求: {time2*1000:.0f}ms (缓存)")
            if time2 > 0:
                print(f"   📊 性能提升: {time1/time2:.1f}x")
        else:
            print("   ⚠️ 请求失败")


async def test_comment_cache():
    """测试评论缓存效果"""
    print("\n2️⃣ 测试评论缓存...")

    async with httpx.AsyncClient() as client:
        # 第一次请求
        start = time.time()
        response1 = await client.get("http://localhost:8000/api/v1/comments/video/1")
        time1 = time.time() - start

        # 第二次请求（缓存）
        start = time.time()
        await client.get("http://localhost:8000/api/v1/comments/video/1")
        time2 = time.time() - start

        if response1.status_code == 200:
            print(f"   ✅ 第一次请求: {time1*1000:.0f}ms")
            print(f"   ✅ 第二次请求: {time2*1000:.0f}ms (缓存)")
            if time2 > 0:
                print(f"   📊 性能提升: {time1/time2:.1f}x")
        else:
            print("   ⚠️ 评论不存在，跳过测试")


async def test_stats_cache():
    """测试统计缓存"""
    print("\n3️⃣ 测试分类统计缓存...")
    print("   ℹ️  需要管理员权限，建议手动测试:")
    print("   GET /api/v1/admin/stats/video-categories")


async def test_health_check():
    """测试健康检查"""
    print("\n4️⃣ 测试健康检查...")

    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/health")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 状态: {data.get('status')}")
            print(f"   ✅ 数据库: {data.get('checks', {}).get('database')}")
            print(f"   ✅ Redis: {data.get('checks', {}).get('redis')}")
        else:
            print(f"   ❌ 健康检查失败: {response.status_code}")


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("🔍 后端优化效果验证")
    print("=" * 60)

    try:
        await test_health_check()
        await test_video_detail_cache()
        await test_comment_cache()
        await test_stats_cache()

        print("\n" + "=" * 60)
        print("✅ 验证完成！")
        print("=" * 60)

        print("\n💡 提示:")
        print("   - 视频详情缓存: 5分钟TTL")
        print("   - 评论缓存: 2分钟TTL")
        print("   - 日志查看: tail -f backend/logs/app_$(date +%Y-%m-%d).log")

    except httpx.ConnectError:
        print("\n❌ 错误: 无法连接到后端服务")
        print("   请先启动后端: make backend-run")
    except Exception as e:
        print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())
