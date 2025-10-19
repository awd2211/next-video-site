#!/usr/bin/env python3
"""
优化检查工具 - 检查代码是否遵循性能最佳实践

Usage:
    python scripts/check_optimization.py
    python scripts/check_optimization.py --path app/api
    python scripts/check_optimization.py --fix
"""

import argparse
import ast
import os
import re
from pathlib import Path

from loguru import logger


class OptimizationChecker:
    """优化检查器"""

    def __init__(self, base_path: str = "app", auto_fix: bool = False):
        self.base_path = Path(base_path)
        self.auto_fix = auto_fix
        self.issues = []
        self.warnings = []
        self.good_practices = []

    def check_all(self):
        """检查所有Python文件"""
        logger.info("🔍 Checking optimization best practices...\n")

        python_files = list(self.base_path.rglob("*.py"))
        logger.info(f"Found {len(python_files)} Python files\n")

        for file_path in python_files:
            if "__pycache__" in str(file_path):
                continue

            self.check_file(file_path)

        self.print_summary()

    def check_file(self, file_path: Path):
        """检查单个文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 各种检查
            self.check_rate_limiting(file_path, content)
            self.check_caching(file_path, content)
            self.check_n_plus_one(file_path, content)
            self.check_batch_operations(file_path, content)
            self.check_error_handling(file_path, content)
            self.check_profiling(file_path, content)

        except Exception as e:
            logger.error(f"Error checking {file_path}: {e}")

    def check_rate_limiting(self, file_path: Path, content: str):
        """检查是否使用了限流"""
        # 检查API路由文件
        if "/api/" in str(file_path) and "@router." in content:
            # 查找路由装饰器
            route_pattern = r"@router\.(get|post|put|delete|patch)\("
            routes = re.findall(route_pattern, content)

            if routes:
                # 检查是否有limiter装饰器
                has_limiter = "@limiter.limit" in content

                if not has_limiter and len(routes) > 0:
                    self.warnings.append(
                        f"⚠️  {file_path}: {len(routes)} routes without rate limiting"
                    )
                    logger.warning(
                        f"  {file_path.name}: {len(routes)} routes without @limiter.limit"
                    )
                else:
                    self.good_practices.append(
                        f"✅ {file_path.name}: Rate limiting enabled"
                    )

    def check_caching(self, file_path: Path, content: str):
        """检查是否使用了缓存"""
        if "/api/" in str(file_path):
            # 检查是否有数据库查询
            has_query = "select(" in content or "db.execute" in content

            # 检查是否使用缓存
            has_cache = "Cache.get" in content or "@cache_result" in content

            if has_query and not has_cache:
                self.warnings.append(
                    f"⚠️  {file_path}: Database queries without caching"
                )
                logger.warning(f"  {file_path.name}: Consider adding caching")

    def check_n_plus_one(self, file_path: Path, content: str):
        """检查可能的N+1查询问题"""
        if "select(" in content:
            # 检查是否使用了selectinload或joinedload
            has_preload = (
                "selectinload" in content
                or "joinedload" in content
                or "subqueryload" in content
            )

            # 检查是否有关系访问
            has_relationship_access = re.search(
                r"\.\w+\.(categories|tags|actors|directors|comments)", content
            )

            if has_relationship_access and not has_preload:
                self.issues.append(
                    f"❌ {file_path}: Possible N+1 query - use selectinload()"
                )
                logger.error(
                    f"  {file_path.name}: Possible N+1 query - missing selectinload"
                )
            elif has_preload:
                self.good_practices.append(
                    f"✅ {file_path.name}: Using eager loading"
                )

    def check_batch_operations(self, file_path: Path, content: str):
        """检查是否应该使用批量操作"""
        # 检查循环中的数据库操作
        loop_db_pattern = r"for .+ in .+:\s+.*db\.(add|execute|delete)"

        if re.search(loop_db_pattern, content, re.MULTILINE):
            self.warnings.append(
                f"⚠️  {file_path}: Loop with DB operations - consider batch processing"
            )
            logger.warning(
                f"  {file_path.name}: Consider using BatchProcessor for loops"
            )

    def check_error_handling(self, file_path: Path, content: str):
        """检查错误处理"""
        # 检查是否有裸except
        if re.search(r"except\s*:", content):
            self.warnings.append(f"⚠️  {file_path}: Bare except clause found")
            logger.warning(f"  {file_path.name}: Avoid bare except: clauses")

        # 检查是否记录异常
        has_try = "try:" in content
        has_logger = "logger." in content or "logging." in content

        if has_try and not has_logger:
            self.warnings.append(
                f"⚠️  {file_path}: Try/except without logging"
            )

    def check_profiling(self, file_path: Path, content: str):
        """检查是否可以添加性能分析"""
        # 检查复杂函数（超过50行）
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 计算函数行数
                    if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                        lines = node.end_lineno - node.lineno

                        if lines > 50:
                            # 检查是否有profiler装饰器
                            has_profiler = any(
                                "PerformanceProfiler" in ast.get_source_segment(content, d)
                                or "@profile" in ast.get_source_segment(content, d)
                                for d in node.decorator_list
                                if ast.get_source_segment(content, d)
                            )

                            if not has_profiler:
                                self.warnings.append(
                                    f"⚠️  {file_path}:{node.lineno}: Function '{node.name}' "
                                    f"({lines} lines) could benefit from profiling"
                                )

        except SyntaxError:
            pass  # 跳过语法错误的文件

    def print_summary(self):
        """打印检查摘要"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 Optimization Check Summary")
        logger.info("=" * 80)

        # 好的实践
        if self.good_practices:
            logger.info(f"\n✅ GOOD PRACTICES ({len(self.good_practices)}):")
            for practice in self.good_practices[:10]:  # 显示前10个
                logger.info(f"  {practice}")
            if len(self.good_practices) > 10:
                logger.info(f"  ... and {len(self.good_practices) - 10} more")

        # 警告
        if self.warnings:
            logger.warning(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                logger.warning(f"  {warning}")

        # 问题
        if self.issues:
            logger.error(f"\n❌ ISSUES ({len(self.issues)}):")
            for issue in self.issues:
                logger.error(f"  {issue}")

        # 建议
        logger.info("\n" + "=" * 80)
        logger.info("💡 Recommendations:")
        logger.info("=" * 80)

        recommendations = []

        if any("rate limiting" in str(w).lower() for w in self.warnings):
            recommendations.append(
                "1. Add @limiter.limit() decorators to API endpoints\n"
                "   Example: @limiter.limit(RateLimitPresets.MODERATE)"
            )

        if any("n+1" in str(i).lower() for i in self.issues):
            recommendations.append(
                "2. Fix N+1 queries using selectinload()\n"
                "   Example: query.options(selectinload(Video.categories))"
            )

        if any("batch" in str(w).lower() for w in self.warnings):
            recommendations.append(
                "3. Use BatchProcessor for bulk operations\n"
                "   Example: await BatchProcessor.batch_insert(db, Model, items)"
            )

        if any("caching" in str(w).lower() for w in self.warnings):
            recommendations.append(
                "4. Add caching for frequently accessed data\n"
                "   Example: @cache_result('key', ttl=300)"
            )

        for i, rec in enumerate(recommendations, 1):
            logger.info(f"\n{rec}")

        # 总分
        total = len(self.good_practices) + len(self.warnings) + len(self.issues)
        if total > 0:
            score = (len(self.good_practices) / total) * 100
            logger.info(f"\nOptimization Score: {score:.1f}%")

            if score >= 80:
                logger.info("Grade: A - Excellent! 🌟")
            elif score >= 60:
                logger.info("Grade: B - Good, but room for improvement")
            elif score >= 40:
                logger.info("Grade: C - Needs attention")
            else:
                logger.info("Grade: D - Major improvements needed")

        logger.info("\n" + "=" * 80 + "\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Optimization Best Practices Checker")
    parser.add_argument(
        "--path", default="app", help="Path to check (default: app)"
    )
    parser.add_argument(
        "--fix", action="store_true", help="Auto-fix issues (not implemented yet)"
    )

    args = parser.parse_args()

    checker = OptimizationChecker(base_path=args.path, auto_fix=args.fix)
    checker.check_all()


if __name__ == "__main__":
    main()
