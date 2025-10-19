#!/usr/bin/env python3
"""
数据库索引建议工具 - 分析数据库并提出索引优化建议

Usage:
    python scripts/suggest_indexes.py
    python scripts/suggest_indexes.py --analyze-queries
    python scripts/suggest_indexes.py --generate-sql
"""

import argparse
import ast
import re
from pathlib import Path
from typing import Any

from loguru import logger
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings


class IndexAnalyzer:
    """索引分析器"""

    def __init__(self):
        self.engine = create_async_engine(settings.DATABASE_URL, echo=False)
        self.suggestions = []
        self.warnings = []
        self.existing_indexes = {}
        self.query_patterns = []

    async def analyze_all(self, analyze_queries: bool = False):
        """执行完整的索引分析"""
        logger.info("🔍 Starting database index analysis...\n")

        # 1. 分析现有索引
        await self.analyze_existing_indexes()

        # 2. 检查外键索引
        await self.check_foreign_key_indexes()

        # 3. 检查常见查询列
        await self.check_common_query_columns()

        # 4. 检查重复索引
        await self.check_duplicate_indexes()

        # 5. 如果开启，分析代码中的查询模式
        if analyze_queries:
            self.analyze_code_queries()

        # 6. 打印报告
        self.print_report()

        await self.engine.dispose()

    async def analyze_existing_indexes(self):
        """分析现有索引"""
        logger.info("📊 Analyzing existing indexes...")

        async with self.engine.connect() as conn:
            # 获取所有表的索引信息
            result = await conn.execute(
                text(
                    """
                SELECT
                    schemaname,
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """
                )
            )

            for row in result:
                table = row.tablename
                if table not in self.existing_indexes:
                    self.existing_indexes[table] = []

                self.existing_indexes[table].append(
                    {"name": row.indexname, "definition": row.indexdef}
                )

        logger.info(
            f"  Found {sum(len(indexes) for indexes in self.existing_indexes.values())} "
            f"indexes across {len(self.existing_indexes)} tables\n"
        )

    async def check_foreign_key_indexes(self):
        """检查外键是否有索引"""
        logger.info("🔗 Checking foreign key indexes...")

        async with self.engine.connect() as conn:
            # 获取所有外键
            result = await conn.execute(
                text(
                    """
                SELECT
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_schema = 'public'
                ORDER BY tc.table_name, kcu.column_name
            """
                )
            )

            missing_fk_indexes = []

            for row in result:
                table = row.table_name
                column = row.column_name

                # 检查是否存在该列的索引
                has_index = False
                if table in self.existing_indexes:
                    for idx in self.existing_indexes[table]:
                        if column in idx["definition"]:
                            has_index = True
                            break

                if not has_index:
                    missing_fk_indexes.append((table, column, row.foreign_table_name))

            if missing_fk_indexes:
                for table, column, ref_table in missing_fk_indexes:
                    self.suggestions.append(
                        {
                            "priority": "HIGH",
                            "type": "MISSING_FK_INDEX",
                            "table": table,
                            "columns": [column],
                            "reason": f"Foreign key to {ref_table} without index",
                            "sql": f'CREATE INDEX idx_{table}_{column} ON "{table}" ("{column}");',
                        }
                    )
                logger.warning(
                    f"  ⚠️  Found {len(missing_fk_indexes)} foreign keys without indexes"
                )
            else:
                logger.info("  ✅ All foreign keys have indexes\n")

    async def check_common_query_columns(self):
        """检查常见查询列的索引"""
        logger.info("🔎 Checking common query column indexes...")

        # 常见的查询列模式
        common_patterns = {
            # 表名: [(列名, 使用场景)]
            "videos": [
                ("status", "Filtering by status"),
                ("is_published", "Filtering published videos"),
                ("view_count", "Sorting by popularity"),
                ("created_at", "Sorting by date"),
                ("updated_at", "Sorting by last update"),
                ("slug", "URL lookup (should be unique)"),
            ],
            "users": [
                ("email", "Login lookup (should be unique)"),
                ("username", "Profile lookup (should be unique)"),
                ("is_active", "Filtering active users"),
                ("created_at", "Sorting by registration date"),
            ],
            "admin_users": [
                ("email", "Admin login (should be unique)"),
                ("username", "Admin lookup (should be unique)"),
                ("is_active", "Filtering active admins"),
                ("is_superadmin", "Permission checks"),
            ],
            "comments": [
                ("video_id", "Finding video comments"),
                ("user_id", "Finding user comments"),
                ("status", "Filtering by moderation status"),
                ("created_at", "Sorting comments"),
                ("parent_id", "Finding replies"),
            ],
            "watch_history": [
                ("user_id", "User history lookup"),
                ("video_id", "Video watch stats"),
                ("watched_at", "Sorting by watch time"),
            ],
            "favorites": [
                ("user_id", "User favorites lookup"),
                ("video_id", "Video favorite count"),
            ],
            "admin_notifications": [
                ("admin_user_id", "User notifications"),
                ("is_read", "Unread notifications"),
                ("created_at", "Sorting notifications"),
                ("notification_type", "Filtering by type"),
            ],
        }

        async with self.engine.connect() as conn:
            for table, columns in common_patterns.items():
                # 检查表是否存在
                table_exists = await conn.execute(
                    text(
                        f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = '{table}'
                    )
                """
                    )
                )

                if not table_exists.scalar():
                    continue

                for column, reason in columns:
                    # 检查列是否存在
                    col_exists = await conn.execute(
                        text(
                            f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns
                            WHERE table_schema = 'public'
                            AND table_name = '{table}'
                            AND column_name = '{column}'
                        )
                    """
                        )
                    )

                    if not col_exists.scalar():
                        continue

                    # 检查是否有索引
                    has_index = False
                    if table in self.existing_indexes:
                        for idx in self.existing_indexes[table]:
                            if column in idx["definition"]:
                                has_index = True
                                break

                    if not has_index:
                        # 特殊处理: slug, email, username 应该是唯一索引
                        is_unique_column = column in ["slug", "email", "username"]

                        self.suggestions.append(
                            {
                                "priority": "MEDIUM" if not is_unique_column else "HIGH",
                                "type": "MISSING_QUERY_INDEX",
                                "table": table,
                                "columns": [column],
                                "reason": reason,
                                "sql": f'CREATE {"UNIQUE " if is_unique_column else ""}INDEX idx_{table}_{column} ON "{table}" ("{column}");',
                            }
                        )

        logger.info(
            f"  Analyzed common query patterns for {len(common_patterns)} tables\n"
        )

    async def check_duplicate_indexes(self):
        """检查重复或冗余的索引"""
        logger.info("🔄 Checking for duplicate indexes...")

        duplicate_count = 0

        for table, indexes in self.existing_indexes.items():
            # 提取每个索引的列信息
            index_columns = {}
            for idx in indexes:
                # 从索引定义中提取列名
                # 例如: CREATE INDEX idx_name ON table (col1, col2)
                match = re.search(r"\(([^)]+)\)", idx["definition"])
                if match:
                    cols = [c.strip().strip('"') for c in match.group(1).split(",")]
                    index_columns[idx["name"]] = cols

            # 检查重复
            checked = set()
            for idx1_name, cols1 in index_columns.items():
                if idx1_name in checked:
                    continue

                for idx2_name, cols2 in index_columns.items():
                    if idx1_name == idx2_name or idx2_name in checked:
                        continue

                    # 完全相同的索引
                    if cols1 == cols2:
                        self.warnings.append(
                            f"Duplicate indexes on {table}: {idx1_name} and {idx2_name} "
                            f"both index {cols1}"
                        )
                        duplicate_count += 1
                        checked.add(idx2_name)

                    # 一个索引是另一个的前缀（可能冗余）
                    elif len(cols1) < len(cols2) and cols2[: len(cols1)] == cols1:
                        self.warnings.append(
                            f"Potentially redundant: {table}.{idx1_name} {cols1} "
                            f"is prefix of {idx2_name} {cols2}"
                        )

        if duplicate_count > 0:
            logger.warning(f"  ⚠️  Found {duplicate_count} duplicate indexes")
        else:
            logger.info("  ✅ No duplicate indexes found\n")

    def analyze_code_queries(self):
        """分析代码中的查询模式"""
        logger.info("📝 Analyzing query patterns in code...")

        # 扫描所有Python文件
        api_path = Path("app/api")
        admin_path = Path("app/admin")

        query_patterns = []

        for path in [api_path, admin_path]:
            if not path.exists():
                continue

            for py_file in path.rglob("*.py"):
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    # 查找 filter_by 和 filter 模式
                    filter_patterns = re.findall(
                        r"\.filter\((\w+)\.(\w+)\s*==", content
                    )
                    filter_by_patterns = re.findall(r"\.filter_by\((\w+)=", content)

                    # 查找 order_by 模式
                    order_patterns = re.findall(r"\.order_by\((\w+)\.(\w+)", content)

                    query_patterns.extend(filter_patterns)
                    query_patterns.extend(
                        [(None, col) for col in filter_by_patterns]
                    )
                    query_patterns.extend(order_patterns)

                except Exception as e:
                    logger.warning(f"Error reading {py_file}: {e}")

        # 统计查询模式
        pattern_counts = {}
        for model, column in query_patterns:
            if column:
                key = f"{model or 'Unknown'}.{column}"
                pattern_counts[key] = pattern_counts.get(key, 0) + 1

        # 找出频繁查询但可能缺少索引的列
        for pattern, count in sorted(
            pattern_counts.items(), key=lambda x: x[1], reverse=True
        ):
            if count >= 3:  # 出现3次以上
                logger.info(f"  Frequent query pattern: {pattern} ({count} times)")

        logger.info(f"  Analyzed {len(query_patterns)} query patterns in code\n")

    def print_report(self):
        """打印分析报告"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 Database Index Analysis Report")
        logger.info("=" * 80)

        # 现有索引统计
        total_indexes = sum(len(indexes) for indexes in self.existing_indexes.values())
        logger.info(f"\n📈 Current State:")
        logger.info(f"  Total tables: {len(self.existing_indexes)}")
        logger.info(f"  Total indexes: {total_indexes}")

        # 建议
        if self.suggestions:
            logger.info(f"\n💡 INDEX SUGGESTIONS ({len(self.suggestions)}):\n")

            # 按优先级分组
            high_priority = [s for s in self.suggestions if s["priority"] == "HIGH"]
            medium_priority = [
                s for s in self.suggestions if s["priority"] == "MEDIUM"
            ]

            if high_priority:
                logger.error(f"🔴 HIGH PRIORITY ({len(high_priority)}):")
                for s in high_priority:
                    logger.error(f"\n  Table: {s['table']}")
                    logger.error(f"  Columns: {', '.join(s['columns'])}")
                    logger.error(f"  Reason: {s['reason']}")
                    logger.error(f"  SQL: {s['sql']}")

            if medium_priority:
                logger.warning(f"\n🟡 MEDIUM PRIORITY ({len(medium_priority)}):")
                for s in medium_priority[:10]:  # 只显示前10个
                    logger.warning(f"\n  Table: {s['table']}")
                    logger.warning(f"  Columns: {', '.join(s['columns'])}")
                    logger.warning(f"  Reason: {s['reason']}")
                    logger.warning(f"  SQL: {s['sql']}")

                if len(medium_priority) > 10:
                    logger.warning(
                        f"\n  ... and {len(medium_priority) - 10} more suggestions"
                    )

        else:
            logger.info("\n✅ No index suggestions - database is well optimized!")

        # 警告
        if self.warnings:
            logger.warning(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                logger.warning(f"  {warning}")

        # 总结
        logger.info("\n" + "=" * 80)
        logger.info("📝 Summary:")
        logger.info("=" * 80)

        if self.suggestions:
            logger.info(
                f"\n✅ Found {len(self.suggestions)} opportunities for optimization"
            )
            logger.info(
                "\n💡 Recommendations:\n"
                "  1. Add indexes for foreign keys first (HIGH priority)\n"
                "  2. Add indexes for frequently queried columns\n"
                "  3. Consider composite indexes for multi-column queries\n"
                "  4. Monitor index usage after creation\n"
                "  5. Remove unused indexes to save storage"
            )
        else:
            logger.info("\n🎉 Your database indexes are well optimized!")

        logger.info("\n" + "=" * 80 + "\n")


async def generate_migration_sql(analyzer: IndexAnalyzer):
    """生成迁移SQL文件"""
    if not analyzer.suggestions:
        logger.info("No suggestions to generate SQL for.")
        return

    sql_lines = [
        "-- Database Index Optimization Migration",
        "-- Generated by suggest_indexes.py",
        "-- Review and test before applying to production!\n",
    ]

    # 按优先级分组
    high_priority = [s for s in analyzer.suggestions if s["priority"] == "HIGH"]
    medium_priority = [s for s in analyzer.suggestions if s["priority"] == "MEDIUM"]

    if high_priority:
        sql_lines.append("-- HIGH PRIORITY INDEXES")
        sql_lines.append("-- These should be created immediately\n")
        for s in high_priority:
            sql_lines.append(f"-- {s['reason']}")
            sql_lines.append(s["sql"])
            sql_lines.append("")

    if medium_priority:
        sql_lines.append("\n-- MEDIUM PRIORITY INDEXES")
        sql_lines.append("-- Review and add based on actual query patterns\n")
        for s in medium_priority:
            sql_lines.append(f"-- {s['reason']}")
            sql_lines.append(s["sql"])
            sql_lines.append("")

    sql_content = "\n".join(sql_lines)

    # 保存到文件
    output_file = Path("scripts/suggested_indexes.sql")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(sql_content)

    logger.info(f"✅ Generated SQL file: {output_file}")
    logger.info(
        "⚠️  IMPORTANT: Review and test the SQL before applying to production!"
    )


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Database Index Suggestion Tool")
    parser.add_argument(
        "--analyze-queries",
        action="store_true",
        help="Analyze query patterns in code",
    )
    parser.add_argument(
        "--generate-sql", action="store_true", help="Generate migration SQL file"
    )

    args = parser.parse_args()

    analyzer = IndexAnalyzer()
    await analyzer.analyze_all(analyze_queries=args.analyze_queries)

    if args.generate_sql:
        await generate_migration_sql(analyzer)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
