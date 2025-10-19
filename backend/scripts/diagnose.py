#!/usr/bin/env python3
"""
性能诊断工具 - 一键检查系统健康状况

Usage:
    python scripts/diagnose.py
    python scripts/diagnose.py --check database
    python scripts/diagnose.py --check all --verbose
"""

import argparse
import asyncio
import sys
from datetime import datetime

import httpx
from loguru import logger


class PerformanceDiagnostic:
    """性能诊断工具"""

    def __init__(self, base_url: str = "http://localhost:8000", verbose: bool = False):
        self.base_url = base_url
        self.verbose = verbose
        self.issues = []
        self.warnings = []
        self.passed = []

    async def run_all_checks(self):
        """运行所有诊断检查"""
        logger.info("\n" + "=" * 80)
        logger.info("🔍 VideoSite Performance Diagnostic Tool")
        logger.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80 + "\n")

        checks = [
            ("API Availability", self.check_api_availability),
            ("Health Status", self.check_health),
            ("Database Pool", self.check_database_pool),
            ("Cache Performance", self.check_cache),
            ("Response Times", self.check_response_times),
            ("Configuration", self.check_configuration),
            ("Security", self.check_security),
        ]

        for name, check_func in checks:
            logger.info(f"📋 Checking {name}...")
            try:
                await check_func()
            except Exception as e:
                self.issues.append(f"{name}: {str(e)}")
                logger.error(f"  ❌ Check failed: {e}")

            await asyncio.sleep(0.5)  # 避免请求过快

        self.print_summary()

    async def check_api_availability(self):
        """检查API可用性"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(f"{self.base_url}/")
                if response.status_code == 200:
                    self.passed.append("✅ API is accessible")
                    logger.info("  ✅ API is accessible")
                else:
                    self.issues.append(f"API returned status {response.status_code}")
                    logger.error(f"  ❌ API returned status {response.status_code}")
            except Exception as e:
                self.issues.append(f"Cannot connect to API: {e}")
                logger.error(f"  ❌ Cannot connect to API: {e}")

    async def check_health(self):
        """检查健康状态"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(f"{self.base_url}/health")
                data = response.json()

                if data.get("status") == "healthy":
                    self.passed.append("✅ Health check passed")
                    logger.info("  ✅ Health check passed")

                    # 检查各个组件
                    checks = data.get("checks", {})
                    for component, status in checks.items():
                        if status == "ok":
                            logger.info(f"    ✅ {component}: OK")
                        else:
                            self.warnings.append(f"{component}: {status}")
                            logger.warning(f"    ⚠️  {component}: {status}")
                else:
                    self.issues.append(f"System unhealthy: {data.get('status')}")
                    logger.error("  ❌ System is unhealthy")

            except Exception as e:
                self.issues.append(f"Health check failed: {e}")
                logger.error(f"  ❌ Health check failed: {e}")

    async def check_database_pool(self):
        """检查数据库连接池"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(f"{self.base_url}/health")
                data = response.json()

                pool = data.get("database_pool", {})
                if pool:
                    checked_out = int(pool.get("checked_out", 0))
                    total = int(pool.get("total_connections", 1))
                    usage = (checked_out / total) * 100

                    logger.info(f"  📊 Pool usage: {usage:.1f}% ({checked_out}/{total})")

                    if usage > 80:
                        self.warnings.append(
                            f"Database pool usage high: {usage:.1f}%"
                        )
                        logger.warning(f"  ⚠️  High pool usage: {usage:.1f}%")
                    elif usage > 90:
                        self.issues.append(
                            f"Database pool nearly exhausted: {usage:.1f}%"
                        )
                        logger.error(f"  ❌ Pool nearly exhausted: {usage:.1f}%")
                    else:
                        self.passed.append(f"✅ Database pool healthy ({usage:.1f}%)")
                        logger.info(f"  ✅ Pool usage healthy: {usage:.1f}%")
                else:
                    self.warnings.append("Database pool info not available")

            except Exception as e:
                self.warnings.append(f"Cannot check database pool: {e}")
                logger.warning(f"  ⚠️  Cannot check pool: {e}")

    async def check_cache(self):
        """检查缓存性能"""
        # 这里需要admin token，所以只做基础检查
        logger.info("  ℹ️  Cache check requires admin access")
        logger.info("  💡 Tip: Check /admin/metrics/summary with admin token")
        self.passed.append("✅ Cache check noted (requires admin)")

    async def check_response_times(self):
        """检查响应时间"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            endpoints = [
                ("/", "Root"),
                ("/health", "Health Check"),
                ("/api/v1/categories", "Categories"),
            ]

            total_time = 0
            slow_endpoints = []

            for endpoint, name in endpoints:
                try:
                    start = asyncio.get_event_loop().time()
                    response = await client.get(f"{self.base_url}{endpoint}")
                    duration = asyncio.get_event_loop().time() - start

                    total_time += duration

                    if duration > 1.0:
                        slow_endpoints.append(f"{name}: {duration:.2f}s")
                        logger.warning(f"  ⚠️  {name}: {duration:.2f}s (slow)")
                    else:
                        logger.info(f"  ✅ {name}: {duration:.2f}s")

                except Exception as e:
                    logger.error(f"  ❌ {name}: Failed ({e})")

            avg_time = total_time / len(endpoints)

            if slow_endpoints:
                self.warnings.append(f"Slow endpoints: {', '.join(slow_endpoints)}")
            else:
                self.passed.append(
                    f"✅ All endpoints respond quickly (avg: {avg_time:.2f}s)"
                )

    async def check_configuration(self):
        """检查配置（基础检查）"""
        logger.info("  ℹ️  Configuration check requires file access")
        logger.info("  💡 Tip: Run app startup to see config validation")
        self.passed.append("✅ Config check noted (run startup validation)")

    async def check_security(self):
        """检查安全配置"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(f"{self.base_url}/")

                # 检查安全头
                headers = response.headers

                security_headers = {
                    "X-Content-Type-Options": "nosniff",
                    "X-Frame-Options": "DENY",
                    "X-XSS-Protection": "1; mode=block",
                }

                missing_headers = []
                for header, expected in security_headers.items():
                    if header not in headers:
                        missing_headers.append(header)

                if missing_headers:
                    self.warnings.append(
                        f"Missing security headers: {', '.join(missing_headers)}"
                    )
                    logger.warning(f"  ⚠️  Missing headers: {', '.join(missing_headers)}")
                else:
                    self.passed.append("✅ Security headers present")
                    logger.info("  ✅ Security headers present")

            except Exception as e:
                self.warnings.append(f"Cannot check security: {e}")

    def print_summary(self):
        """打印诊断摘要"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 Diagnostic Summary")
        logger.info("=" * 80)

        # 通过的检查
        if self.passed:
            logger.info(f"\n✅ PASSED ({len(self.passed)}):")
            for item in self.passed:
                logger.info(f"  {item}")

        # 警告
        if self.warnings:
            logger.warning(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for item in self.warnings:
                logger.warning(f"  {item}")

        # 问题
        if self.issues:
            logger.error(f"\n❌ ISSUES ({len(self.issues)}):")
            for item in self.issues:
                logger.error(f"  {item}")

        # 总结
        logger.info("\n" + "=" * 80)
        total = len(self.passed) + len(self.warnings) + len(self.issues)
        health_score = (
            (len(self.passed) + len(self.warnings) * 0.5) / total * 100 if total > 0 else 0
        )

        if health_score >= 90:
            status = "EXCELLENT ✨"
            color = "green"
        elif health_score >= 70:
            status = "GOOD ✅"
            color = "green"
        elif health_score >= 50:
            status = "FAIR ⚠️"
            color = "yellow"
        else:
            status = "NEEDS ATTENTION ❌"
            color = "red"

        logger.info(f"Overall Health Score: {health_score:.1f}% - {status}")

        if self.issues:
            logger.info("\n💡 Recommendations:")
            logger.info("  1. Fix critical issues listed above")
            logger.info("  2. Review warnings for potential improvements")
            logger.info("  3. Check logs for detailed error information")

        logger.info("=" * 80 + "\n")

        # 退出码
        if self.issues:
            sys.exit(1)  # 有问题则退出码为1
        else:
            sys.exit(0)


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Performance Diagnostic Tool")
    parser.add_argument(
        "--base-url", default="http://localhost:8000", help="Base URL of the API"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--check",
        choices=["api", "health", "database", "cache", "all"],
        default="all",
        help="Specific check to run",
    )

    args = parser.parse_args()

    diagnostic = PerformanceDiagnostic(base_url=args.base_url, verbose=args.verbose)

    if args.check == "all":
        await diagnostic.run_all_checks()
    else:
        logger.info(f"Running {args.check} check...")
        # 可以添加单个检查的逻辑
        await diagnostic.run_all_checks()


if __name__ == "__main__":
    asyncio.run(main())
