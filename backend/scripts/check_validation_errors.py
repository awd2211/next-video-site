#!/usr/bin/env python3
"""
验证错误诊断工具 - 检查和调试API验证错误

Usage:
    python scripts/check_validation_errors.py
    python scripts/check_validation_errors.py --endpoint /api/v1/admin/media
    python scripts/check_validation_errors.py --recent 50
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from loguru import logger


class ValidationErrorAnalyzer:
    """验证错误分析器"""

    def __init__(self, log_file: str = "uvicorn.log"):
        self.log_file = Path(log_file)
        self.validation_errors = []

    def parse_log_file(self, recent: int = 100):
        """解析日志文件，提取验证错误"""
        if not self.log_file.exists():
            logger.warning(f"Log file not found: {self.log_file}")
            return

        logger.info(f"📖 Parsing log file: {self.log_file}")

        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # 只读取最后N行
            lines = lines[-recent:] if len(lines) > recent else lines

            # 查找验证错误
            i = 0
            while i < len(lines):
                line = lines[i]

                # 检测验证错误关键词
                if "validation" in line.lower() and ("failed" in line.lower() or "error" in line.lower()):
                    error_entry = self._extract_error_details(lines, i)
                    if error_entry:
                        self.validation_errors.append(error_entry)

                # 检测422状态码（验证错误）
                if "422" in line:
                    error_entry = self._extract_error_details(lines, i)
                    if error_entry:
                        self.validation_errors.append(error_entry)

                i += 1

            logger.info(f"Found {len(self.validation_errors)} validation errors")

        except Exception as e:
            logger.error(f"Error parsing log file: {e}")

    def _extract_error_details(self, lines, start_index):
        """从日志行中提取错误详情"""
        try:
            error_line = lines[start_index]

            # 尝试提取时间戳
            timestamp_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", error_line)
            timestamp = timestamp_match.group(1) if timestamp_match else "Unknown"

            # 尝试提取路径
            path_match = re.search(r'"(GET|POST|PUT|DELETE|PATCH) ([^"]+)"', error_line)
            method = path_match.group(1) if path_match else "Unknown"
            path = path_match.group(2) if path_match else "Unknown"

            # 尝试提取错误信息（接下来的几行）
            error_details = []
            for j in range(start_index, min(start_index + 10, len(lines))):
                if "field" in lines[j].lower() or "message" in lines[j].lower():
                    error_details.append(lines[j].strip())

            return {
                "timestamp": timestamp,
                "method": method,
                "path": path,
                "error_line": error_line.strip(),
                "details": error_details[:5]  # 最多5行详情
            }

        except Exception:
            return None

    def analyze_common_errors(self):
        """分析常见错误模式"""
        if not self.validation_errors:
            logger.info("✅ No validation errors found!")
            return

        logger.info(f"\n{'='*80}")
        logger.info("📊 Validation Error Analysis")
        logger.info(f"{'='*80}\n")

        # 按路径分组
        errors_by_path = {}
        for error in self.validation_errors:
            path = error["path"]
            if path not in errors_by_path:
                errors_by_path[path] = []
            errors_by_path[path].append(error)

        # 打印按路径分组的错误
        logger.info(f"🔍 Errors by Endpoint ({len(errors_by_path)} unique endpoints):\n")

        for path, errors in sorted(errors_by_path.items(), key=lambda x: len(x[1]), reverse=True):
            logger.error(f"  {path} ({len(errors)} errors)")

        # 打印详细错误信息
        logger.info(f"\n📋 Recent Validation Errors (last {min(10, len(self.validation_errors))}):\n")

        for i, error in enumerate(self.validation_errors[-10:], 1):
            logger.info(f"{'─'*80}")
            logger.error(f"{i}. [{error['timestamp']}] {error['method']} {error['path']}")
            logger.info(f"   Error: {error['error_line']}")

            if error["details"]:
                logger.info("   Details:")
                for detail in error["details"]:
                    logger.info(f"     {detail}")

        # 提供建议
        logger.info(f"\n{'='*80}")
        logger.info("💡 Troubleshooting Tips:")
        logger.info(f"{'='*80}\n")

        tips = [
            "1. Check request body/query parameters match the API schema",
            "2. Verify required fields are being sent",
            "3. Check data types (int vs string, etc.)",
            "4. Verify enum values are correct",
            "5. Check for typos in field names",
            "6. Enable DEBUG mode to see detailed validation errors",
        ]

        for tip in tips:
            logger.info(f"  {tip}")

        logger.info("\n" + "="*80 + "\n")

    def check_specific_endpoint(self, endpoint: str):
        """检查特定端点的验证错误"""
        endpoint_errors = [
            e for e in self.validation_errors
            if endpoint in e["path"]
        ]

        if not endpoint_errors:
            logger.info(f"✅ No validation errors found for: {endpoint}")
            return

        logger.info(f"\n🔍 Validation Errors for: {endpoint}")
        logger.info(f"Found {len(endpoint_errors)} errors\n")

        for i, error in enumerate(endpoint_errors, 1):
            logger.error(f"{i}. [{error['timestamp']}] {error['method']} {error['path']}")
            logger.info(f"   {error['error_line']}")

            if error["details"]:
                for detail in error["details"]:
                    logger.info(f"   {detail}")
            logger.info("")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Validation Error Diagnostic Tool")
    parser.add_argument(
        "--log-file",
        default="uvicorn.log",
        help="Path to log file (default: uvicorn.log)"
    )
    parser.add_argument(
        "--endpoint",
        help="Filter errors by specific endpoint"
    )
    parser.add_argument(
        "--recent",
        type=int,
        default=500,
        help="Number of recent log lines to analyze (default: 500)"
    )

    args = parser.parse_args()

    analyzer = ValidationErrorAnalyzer(log_file=args.log_file)
    analyzer.parse_log_file(recent=args.recent)

    if args.endpoint:
        analyzer.check_specific_endpoint(args.endpoint)
    else:
        analyzer.analyze_common_errors()


if __name__ == "__main__":
    main()
