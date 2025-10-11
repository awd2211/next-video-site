"""
慢查询监控中间件
记录执行时间超过阈值的数据库查询
"""

import logging
import time

from sqlalchemy import event

from app.database import async_engine

logger = logging.getLogger(__name__)

# 慢查询阈值（秒）
SLOW_QUERY_THRESHOLD = 0.5  # 500ms


class QueryMonitor:
    """查询监控器"""

    def __init__(self, threshold: float = SLOW_QUERY_THRESHOLD):
        self.threshold = threshold
        self.enabled = False

    def enable(self):
        """启用查询监控"""
        if self.enabled:
            return

        # 注册SQLAlchemy事件监听器
        @event.listens_for(async_engine.sync_engine, "before_cursor_execute")
        def receive_before_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            """查询执行前"""
            conn.info.setdefault("query_start_time", []).append(time.time())

        @event.listens_for(async_engine.sync_engine, "after_cursor_execute")
        def receive_after_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            """查询执行后"""
            total_time = time.time() - conn.info["query_start_time"].pop()

            # 如果执行时间超过阈值，记录慢查询
            if total_time > self.threshold:
                # 清理SQL语句（移除多余空格和换行）
                clean_statement = " ".join(statement.split())

                # 记录慢查询日志
                logger.warning(
                    f"SLOW QUERY ({total_time:.3f}s): {clean_statement[:500]}",
                    extra={
                        "execution_time": total_time,
                        "statement": clean_statement,
                        "parameters": str(parameters)[:200] if parameters else None,
                        "threshold": self.threshold,
                    },
                )

        self.enabled = True
        logger.info(f"Query monitor enabled with threshold: {self.threshold}s")

    def disable(self):
        """禁用查询监控"""
        # SQLAlchemy事件不支持直接移除，需要在应用重启时生效
        self.enabled = False
        logger.info("Query monitor disabled (takes effect on restart)")


# 全局查询监控器实例
query_monitor = QueryMonitor()


def setup_query_monitoring(threshold: float = SLOW_QUERY_THRESHOLD):
    """
    设置查询监控

    Args:
        threshold: 慢查询阈值（秒）
    """
    query_monitor.threshold = threshold
    query_monitor.enable()
