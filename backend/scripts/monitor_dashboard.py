#!/usr/bin/env python3
"""
性能监控仪表板 - 实时显示系统性能指标

Usage:
    python scripts/monitor_dashboard.py
    python scripts/monitor_dashboard.py --refresh 5
    python scripts/monitor_dashboard.py --admin-token <token>

Requirements:
    pip install httpx rich
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime
from typing import Any

import httpx
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class PerformanceDashboard:
    """性能监控仪表板"""

    def __init__(
        self, base_url: str = "http://localhost:8000", admin_token: str | None = None
    ):
        self.base_url = base_url
        self.admin_token = admin_token
        self.console = Console()
        self.client = httpx.AsyncClient(timeout=10.0)

        # 数据缓存
        self.health_data = {}
        self.metrics_data = {}
        self.profiler_data = {}
        self.error_count = 0
        self.last_update = None

    async def fetch_health(self) -> dict[str, Any]:
        """获取健康状态"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            self.error_count += 1
            return {"status": "error", "error": str(e)}

    async def fetch_metrics(self) -> dict[str, Any]:
        """获取指标数据（需要admin token）"""
        if not self.admin_token:
            return {}

        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(
                f"{self.base_url}/api/v1/admin/metrics/summary", headers=headers
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    async def fetch_profiler(self) -> dict[str, Any]:
        """获取性能分析数据（需要admin token）"""
        if not self.admin_token:
            return {}

        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(
                f"{self.base_url}/api/v1/admin/profiler/functions?top_n=5",
                headers=headers,
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    async def update_data(self):
        """更新所有数据"""
        self.health_data = await self.fetch_health()
        self.metrics_data = await self.fetch_metrics()
        self.profiler_data = await self.fetch_profiler()
        self.last_update = datetime.now()

    def create_header(self) -> Panel:
        """创建头部"""
        title = Text("VideoSite Performance Dashboard", style="bold white on blue")

        info = Text()
        info.append(f"URL: {self.base_url}  |  ", style="dim")
        info.append(
            f"Updated: {self.last_update.strftime('%H:%M:%S') if self.last_update else 'N/A'}  |  ",
            style="dim",
        )
        info.append(
            f"Admin: {'✅' if self.admin_token else '❌'}",
            style="green" if self.admin_token else "red",
        )

        return Panel(
            Text.assemble(title, "\n", info), style="bold white", padding=(0, 2)
        )

    def create_system_health(self) -> Panel:
        """创建系统健康面板"""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="white")

        # 系统状态
        status = self.health_data.get("status", "unknown")
        status_color = (
            "green" if status == "healthy" else "red" if status == "error" else "yellow"
        )
        status_emoji = "✅" if status == "healthy" else "❌" if status == "error" else "⚠️"

        table.add_row("Status", f"[{status_color}]{status_emoji} {status.upper()}[/]")

        # 组件检查
        checks = self.health_data.get("checks", {})
        if checks:
            for component, check_status in checks.items():
                check_color = "green" if check_status == "ok" else "red"
                check_emoji = "✅" if check_status == "ok" else "❌"
                table.add_row(
                    f"  {component.title()}",
                    f"[{check_color}]{check_emoji} {check_status}[/]",
                )

        # 数据库连接池
        pool = self.health_data.get("database_pool", {})
        if pool:
            checked_out = int(pool.get("checked_out", 0))
            total = int(pool.get("total_connections", 0) or pool.get("pool_size", 0))
            overflow = int(pool.get("overflow", 0))

            if total > 0:
                usage_pct = (checked_out / total) * 100
                usage_color = (
                    "green"
                    if usage_pct < 50
                    else "yellow" if usage_pct < 80 else "red"
                )

                table.add_row(
                    "Pool Usage",
                    f"[{usage_color}]{checked_out}/{total} ({usage_pct:.1f}%)[/]",
                )

                if overflow > 0:
                    table.add_row("Pool Overflow", f"[yellow]{overflow}[/]")

        return Panel(table, title="[bold]System Health[/]", border_style="green")

    def create_api_metrics(self) -> Panel:
        """创建API指标面板"""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="white")

        if not self.admin_token:
            table.add_row(
                "Status", "[yellow]⚠️ Admin token required for detailed metrics[/]"
            )
        elif "error" in self.metrics_data:
            table.add_row("Error", f"[red]❌ {self.metrics_data['error']}[/]")
        else:
            # API请求统计
            api = self.metrics_data.get("api", {})
            total_requests = api.get("total_requests", 0)
            table.add_row("Total Requests", f"[white]{total_requests:,}[/]")

            # 视频浏览量
            videos = self.metrics_data.get("videos", {})
            total_views = int(videos.get("total_views", 0))
            table.add_row("Total Views", f"[white]{total_views:,}[/]")

            # 缓存统计
            cache = self.metrics_data.get("cache", {})
            hit_rate = cache.get("hit_rate", "N/A")
            total_cache = cache.get("total_requests", "N/A")

            if hit_rate != "N/A":
                hit_rate_num = float(hit_rate)
                hit_rate_color = (
                    "green"
                    if hit_rate_num >= 80
                    else "yellow" if hit_rate_num >= 50 else "red"
                )
                table.add_row(
                    "Cache Hit Rate", f"[{hit_rate_color}]{hit_rate}%[/]"
                )
            else:
                table.add_row("Cache Hit Rate", "[dim]N/A[/]")

            if total_cache != "N/A":
                table.add_row("Cache Requests", f"[white]{total_cache}[/]")

        return Panel(table, title="[bold]API Metrics[/]", border_style="blue")

    def create_performance(self) -> Panel:
        """创建性能分析面板"""
        if not self.admin_token:
            text = Text("⚠️ Admin token required for profiler data", style="yellow")
            return Panel(text, title="[bold]Top Functions[/]", border_style="yellow")

        if "error" in self.profiler_data:
            text = Text(f"❌ {self.profiler_data['error']}", style="red")
            return Panel(text, title="[bold]Top Functions[/]", border_style="red")

        table = Table(show_header=True, box=None, padding=(0, 1))
        table.add_column("Function", style="cyan", width=30, overflow="fold")
        table.add_column("Calls", style="yellow", justify="right", width=8)
        table.add_column("Avg (ms)", style="green", justify="right", width=10)
        table.add_column("Total (s)", style="magenta", justify="right", width=10)

        functions = self.profiler_data.get("functions", [])

        if not functions:
            table.add_row("No data", "-", "-", "-")
        else:
            for func in functions[:5]:  # Top 5
                name = func.get("function_name", "unknown")
                # 截断长函数名
                if len(name) > 28:
                    name = name[:25] + "..."

                calls = func.get("call_count", 0)
                avg_time_ms = func.get("avg_time", 0) * 1000
                total_time_s = func.get("total_time", 0)

                # 根据平均时间着色
                avg_color = (
                    "green"
                    if avg_time_ms < 100
                    else "yellow" if avg_time_ms < 500 else "red"
                )

                table.add_row(
                    name,
                    f"{calls:,}",
                    f"[{avg_color}]{avg_time_ms:.2f}[/]",
                    f"{total_time_s:.2f}",
                )

        return Panel(table, title="[bold]Top Functions[/]", border_style="magenta")

    def create_alerts(self) -> Panel:
        """创建告警面板"""
        alerts = []

        # 检查系统状态
        if self.health_data.get("status") != "healthy":
            alerts.append(("🔴 CRITICAL", "System is unhealthy!", "red"))

        # 检查连接池
        pool = self.health_data.get("database_pool", {})
        if pool:
            checked_out = int(pool.get("checked_out", 0))
            total = int(pool.get("total_connections", 0) or pool.get("pool_size", 0))

            if total > 0:
                usage_pct = (checked_out / total) * 100
                if usage_pct > 90:
                    alerts.append(
                        (
                            "🔴 CRITICAL",
                            f"DB pool nearly exhausted ({usage_pct:.1f}%)",
                            "red",
                        )
                    )
                elif usage_pct > 80:
                    alerts.append(
                        (
                            "🟡 WARNING",
                            f"DB pool usage high ({usage_pct:.1f}%)",
                            "yellow",
                        )
                    )

        # 检查缓存命中率
        cache = self.metrics_data.get("cache", {})
        if cache.get("hit_rate") != "N/A":
            hit_rate = float(cache.get("hit_rate", 100))
            if hit_rate < 50:
                alerts.append(
                    (
                        "🟡 WARNING",
                        f"Low cache hit rate ({hit_rate:.1f}%)",
                        "yellow",
                    )
                )

        # 检查慢函数
        functions = self.profiler_data.get("functions", [])
        for func in functions[:3]:
            avg_time_ms = func.get("avg_time", 0) * 1000
            if avg_time_ms > 500:
                alerts.append(
                    (
                        "🟡 WARNING",
                        f"Slow function: {func['function_name'][:30]} ({avg_time_ms:.0f}ms)",
                        "yellow",
                    )
                )

        # 检查连接错误
        if self.error_count > 0:
            alerts.append(
                (
                    "🟡 WARNING",
                    f"{self.error_count} connection errors since start",
                    "yellow",
                )
            )

        # 创建表格
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Level", width=15)
        table.add_column("Message", style="white")

        if not alerts:
            table.add_row("✅ ALL CLEAR", "[green]No alerts[/]")
        else:
            for level, message, color in alerts[-5:]:  # 最多显示5个
                table.add_row(f"[{color}]{level}[/]", f"[{color}]{message}[/]")

        return Panel(table, title="[bold]Alerts[/]", border_style="red")

    def create_layout(self) -> Layout:
        """创建布局"""
        layout = Layout()

        # 主布局
        layout.split_column(
            Layout(name="header", size=4),
            Layout(name="body"),
            Layout(name="footer", size=3),
        )

        # Body分为左右两列
        layout["body"].split_row(Layout(name="left"), Layout(name="right"))

        # 左列
        layout["left"].split_column(
            Layout(name="health", ratio=2), Layout(name="alerts", ratio=1)
        )

        # 右列
        layout["right"].split_column(
            Layout(name="metrics", ratio=1), Layout(name="performance", ratio=2)
        )

        return layout

    def render(self) -> Layout:
        """渲染仪表板"""
        layout = self.create_layout()

        # 填充布局
        layout["header"].update(self.create_header())
        layout["health"].update(self.create_system_health())
        layout["metrics"].update(self.create_api_metrics())
        layout["performance"].update(self.create_performance())
        layout["alerts"].update(self.create_alerts())

        # Footer
        footer_text = Text()
        footer_text.append("Press ", style="dim")
        footer_text.append("Ctrl+C", style="bold")
        footer_text.append(" to exit  |  ", style="dim")

        if not self.admin_token:
            footer_text.append(
                "⚠️ Use --admin-token to see full metrics", style="yellow"
            )
        else:
            footer_text.append("✅ Full metrics enabled", style="green")

        layout["footer"].update(Panel(footer_text, style="dim"))

        return layout

    async def run(self, refresh_interval: int = 3):
        """运行仪表板"""
        self.console.print(
            "\n[bold green]Starting Performance Dashboard...[/]\n", justify="center"
        )

        try:
            with Live(
                self.render(), refresh_per_second=1, console=self.console
            ) as live:
                while True:
                    await self.update_data()
                    live.update(self.render())
                    await asyncio.sleep(refresh_interval)

        except KeyboardInterrupt:
            self.console.print(
                "\n\n[bold yellow]Dashboard stopped by user[/]\n", justify="center"
            )
        finally:
            await self.client.aclose()


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Performance Monitoring Dashboard")
    parser.add_argument(
        "--base-url", default="http://localhost:8000", help="Base URL of the API"
    )
    parser.add_argument(
        "--admin-token",
        default=None,
        help="Admin JWT token for accessing metrics (optional)",
    )
    parser.add_argument(
        "--refresh",
        type=int,
        default=3,
        help="Refresh interval in seconds (default: 3)",
    )

    args = parser.parse_args()

    # 检查admin token环境变量
    admin_token = args.admin_token or os.getenv("ADMIN_TOKEN")

    dashboard = PerformanceDashboard(base_url=args.base_url, admin_token=admin_token)
    await dashboard.run(refresh_interval=args.refresh)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋\n")
        sys.exit(0)
