#!/usr/bin/env python3
"""
API 性能测试脚本
测试各个端点的响应时间和并发性能

Usage:
    python scripts/performance_test.py
    python scripts/performance_test.py --endpoint /api/v1/videos --concurrent 50
"""

import argparse
import asyncio
import statistics
import time
from typing import List

import httpx
from loguru import logger


class PerformanceTester:
    """API性能测试器"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []

    async def test_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        concurrent: int = 10,
        total_requests: int = 100,
        headers: dict | None = None,
        json_data: dict | None = None,
    ) -> dict:
        """
        测试单个端点的性能

        Args:
            endpoint: API端点路径
            method: HTTP方法
            concurrent: 并发请求数
            total_requests: 总请求数
            headers: 请求头
            json_data: 请求body

        Returns:
            性能测试结果
        """
        logger.info(f"\n🔍 Testing {method} {endpoint}")
        logger.info(f"   Concurrent: {concurrent}, Total: {total_requests}")

        durations = []
        errors = 0
        start_time = time.time()

        async with httpx.AsyncClient(timeout=30.0) as client:
            # 创建任务列表
            tasks = []

            for i in range(total_requests):
                task = self._make_request(
                    client, endpoint, method, headers, json_data
                )
                tasks.append(task)

            # 控制并发数
            for i in range(0, len(tasks), concurrent):
                batch = tasks[i : i + concurrent]
                results = await asyncio.gather(*batch, return_exceptions=True)

                for result in results:
                    if isinstance(result, Exception):
                        errors += 1
                        logger.error(f"Request failed: {result}")
                    elif isinstance(result, dict) and "error" in result:
                        errors += 1
                    else:
                        durations.append(result)

        total_time = time.time() - start_time

        # 计算统计数据
        if durations:
            stats = {
                "endpoint": endpoint,
                "method": method,
                "total_requests": total_requests,
                "successful": len(durations),
                "errors": errors,
                "total_time": round(total_time, 2),
                "requests_per_second": round(total_requests / total_time, 2),
                "avg_response_time": round(statistics.mean(durations), 3),
                "min_response_time": round(min(durations), 3),
                "max_response_time": round(max(durations), 3),
                "median_response_time": round(statistics.median(durations), 3),
                "p95_response_time": round(
                    statistics.quantiles(durations, n=20)[18], 3
                ),  # 95th percentile
                "p99_response_time": round(
                    statistics.quantiles(durations, n=100)[98], 3
                ),  # 99th percentile
            }
        else:
            stats = {
                "endpoint": endpoint,
                "errors": errors,
                "total_requests": total_requests,
                "successful": 0,
                "message": "All requests failed",
            }

        self.results.append(stats)
        self._print_stats(stats)

        return stats

    async def _make_request(
        self,
        client: httpx.AsyncClient,
        endpoint: str,
        method: str,
        headers: dict | None,
        json_data: dict | None,
    ) -> float | dict:
        """执行单个HTTP请求并测量时间"""
        url = f"{self.base_url}{endpoint}"
        start = time.time()

        try:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=json_data)
            elif method == "PUT":
                response = await client.put(url, headers=headers, json=json_data)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                return {"error": f"Unsupported method: {method}"}

            duration = time.time() - start

            if response.status_code >= 400:
                return {"error": f"HTTP {response.status_code}"}

            return duration

        except Exception as e:
            return {"error": str(e)}

    def _print_stats(self, stats: dict):
        """打印测试统计"""
        logger.info("\n" + "=" * 60)
        logger.info(f"📊 Results for {stats['endpoint']}")
        logger.info("=" * 60)

        if "message" in stats:
            logger.error(f"❌ {stats['message']}")
            return

        logger.info(f"✅ Successful: {stats['successful']}/{stats['total_requests']}")
        logger.info(f"❌ Errors: {stats['errors']}")
        logger.info(f"⏱️  Total Time: {stats['total_time']}s")
        logger.info(f"🚀 Throughput: {stats['requests_per_second']} req/s")
        logger.info("\nResponse Times:")
        logger.info(f"  Average: {stats['avg_response_time']}s")
        logger.info(f"  Median:  {stats['median_response_time']}s")
        logger.info(
            f"  Min/Max: {stats['min_response_time']}s / {stats['max_response_time']}s"
        )
        logger.info(f"  P95:     {stats['p95_response_time']}s")
        logger.info(f"  P99:     {stats['p99_response_time']}s")
        logger.info("=" * 60 + "\n")

    def print_summary(self):
        """打印所有测试的总结"""
        if not self.results:
            logger.info("No test results available")
            return

        logger.info("\n" + "=" * 80)
        logger.info("📈 Performance Test Summary")
        logger.info("=" * 80)
        logger.info(
            f"{'Endpoint':<40} {'RPS':>10} {'Avg(ms)':>10} {'P95(ms)':>10} {'Errors':>8}"
        )
        logger.info("-" * 80)

        for result in self.results:
            if "message" not in result:
                logger.info(
                    f"{result['endpoint']:<40} "
                    f"{result['requests_per_second']:>10.1f} "
                    f"{result['avg_response_time']*1000:>10.1f} "
                    f"{result['p95_response_time']*1000:>10.1f} "
                    f"{result['errors']:>8}"
                )

        logger.info("=" * 80 + "\n")


async def run_standard_tests():
    """运行标准性能测试套件"""
    tester = PerformanceTester()

    # 测试配置
    tests = [
        {
            "endpoint": "/",
            "concurrent": 50,
            "total_requests": 200,
            "description": "Root endpoint",
        },
        {
            "endpoint": "/health",
            "concurrent": 50,
            "total_requests": 200,
            "description": "Health check",
        },
        {
            "endpoint": "/api/v1/videos?page=1&page_size=20",
            "concurrent": 20,
            "total_requests": 100,
            "description": "Video list (cached)",
        },
        {
            "endpoint": "/api/v1/categories",
            "concurrent": 30,
            "total_requests": 150,
            "description": "Categories list",
        },
    ]

    for test in tests:
        logger.info(f"\n🎯 {test['description']}")
        await tester.test_endpoint(
            endpoint=test["endpoint"],
            concurrent=test["concurrent"],
            total_requests=test["total_requests"],
        )

        # 等待一下，避免压垮服务器
        await asyncio.sleep(2)

    # 打印总结
    tester.print_summary()


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="API Performance Testing")
    parser.add_argument(
        "--endpoint", help="Specific endpoint to test", default=None
    )
    parser.add_argument(
        "--concurrent", type=int, help="Concurrent requests", default=10
    )
    parser.add_argument(
        "--total", type=int, help="Total requests", default=100
    )
    parser.add_argument(
        "--base-url",
        help="Base URL",
        default="http://localhost:8000",
    )

    args = parser.parse_args()

    if args.endpoint:
        # 测试单个端点
        tester = PerformanceTester(base_url=args.base_url)
        await tester.test_endpoint(
            endpoint=args.endpoint,
            concurrent=args.concurrent,
            total_requests=args.total,
        )
    else:
        # 运行标准测试套件
        await run_standard_tests()


if __name__ == "__main__":
    logger.info("🚀 Starting API Performance Tests")
    asyncio.run(main())
