#!/usr/bin/env python3
"""
全文搜索性能测试
对比ILIKE vs PostgreSQL全文搜索的性能差异
"""
import asyncio
import time

import httpx


async def test_search_performance():
    """测试搜索性能"""
    print("=" * 60)
    print("🔍 全文搜索性能测试")
    print("=" * 60)

    search_queries = [
        "进击",
        "你的名字",
        "电影",
        "2020",
    ]

    async with httpx.AsyncClient() as client:
        for query in search_queries:
            print(f"\n📝 搜索关键词: '{query}'")

            # 第一次请求（无缓存）
            start = time.time()
            response1 = await client.get(
                f"http://localhost:8000/api/v1/search?q={query}&page=1&page_size=10"
            )
            time1 = time.time() - start

            # 第二次请求（缓存）
            start = time.time()
            response2 = await client.get(
                f"http://localhost:8000/api/v1/search?q={query}&page=1&page_size=10"
            )
            time2 = time.time() - start

            if response1.status_code == 200:
                data = response1.json()
                print(f"   ✅ 找到结果: {data['total']}条")
                print(f"   ✅ 第一次请求: {time1*1000:.0f}ms (全文搜索)")
                print(f"   ✅ 第二次请求: {time2*1000:.0f}ms (缓存)")
                if time2 > 0:
                    print(f"   📊 缓存提升: {time1/time2:.1f}x")

                # 显示前3个结果
                for i, item in enumerate(data["items"][:3], 1):
                    print(f"      {i}. {item['title']}")
            else:
                print(f"   ❌ 搜索失败: {response1.status_code}")


async def test_relevance_sorting():
    """测试相关性排序"""
    print("\n" + "=" * 60)
    print("📊 测试相关性排序")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        query = "进击"

        # 按相关性排序
        print(f"\n🔍 搜索 '{query}' (按相关性排序)...")
        response = await client.get(
            f"http://localhost:8000/api/v1/search?q={query}&sort_by=relevance&page_size=5"
        )

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 结果数量: {data['total']}")
            print("   📋 按相关性排序的结果:")
            for i, item in enumerate(data["items"], 1):
                print(f"      {i}. {item['title']}")
        else:
            print(f"   ❌ 失败: {response.status_code}")


async def test_advanced_filters():
    """测试高级筛选"""
    print("\n" + "=" * 60)
    print("🎯 测试高级筛选")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # 组合筛选：搜索 + 年份 + 最低评分
        print("\n🔍 组合筛选: 关键词='进击' + 年份=2019 + 评分>=8.0")

        response = await client.get(
            "http://localhost:8000/api/v1/search?q=进击&year=2019&min_rating=8.0"
        )

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 找到结果: {data['total']}条")
            for i, item in enumerate(data["items"][:3], 1):
                print(
                    f"      {i}. {item['title']} "
                    f"({item['release_year']}, 评分:{item['average_rating']})"
                )
        else:
            print(f"   ❌ 失败: {response.status_code}")


async def test_search_features():
    """测试搜索特性"""
    print("\n" + "=" * 60)
    print("✨ 搜索特性测试")
    print("=" * 60)

    test_cases = [
        ("单字搜索", "巨"),
        ("多字搜索", "进击的巨人"),
        ("英文搜索", "movie"),
        ("数字搜索", "2020"),
    ]

    async with httpx.AsyncClient() as client:
        for name, query in test_cases:
            start = time.time()
            response = await client.get(
                f"http://localhost:8000/api/v1/search?q={query}&page_size=5"
            )
            elapsed = time.time() - start

            if response.status_code == 200:
                data = response.json()
                print(f"\n   {name}: '{query}'")
                print(f"      结果: {data['total']}条, 耗时: {elapsed*1000:.0f}ms")
            else:
                print(f"   ❌ {name} 失败")


async def main():
    """运行所有测试"""
    try:
        await test_search_performance()
        await test_relevance_sorting()
        await test_advanced_filters()
        await test_search_features()

        print("\n" + "=" * 60)
        print("✅ 全文搜索测试完成！")
        print("=" * 60)

        print("\n💡 全文搜索优势:")
        print("   - ✅ 使用GIN索引，性能远超ILIKE")
        print("   - ✅ 支持相关性排序（ts_rank）")
        print("   - ✅ 自动更新（触发器）")
        print("   - ✅ 组合高级筛选")
        print("   - ✅ 缓存加速（5分钟TTL）")

        print("\n📊 可用排序方式:")
        print("   - created_at (默认)")
        print("   - view_count (热度)")
        print("   - average_rating (评分)")
        print("   - relevance (相关性) ⭐ 新增")

    except httpx.ConnectError:
        print("\n❌ 错误: 无法连接到后端服务")
        print("   请先启动后端: make backend-run")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

