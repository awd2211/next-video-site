"""
智能重试机制
用于处理临时性故障（网络抖动、数据库连接等）
"""

import asyncio
import functools
from typing import Callable, Type

from loguru import logger


class RetryConfig:
    """重试配置"""

    # 默认可重试的异常类型
    RETRYABLE_EXCEPTIONS = (
        ConnectionError,
        TimeoutError,
        asyncio.TimeoutError,
    )

    # 数据库相关异常（需要导入时检查）
    @staticmethod
    def get_db_exceptions():
        """获取数据库相关的可重试异常"""
        try:
            from sqlalchemy.exc import OperationalError, TimeoutError as SQLAlchemyTimeout

            return (OperationalError, SQLAlchemyTimeout)
        except ImportError:
            return tuple()


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[Type[Exception], ...] | None = None,
    on_retry: Callable | None = None,
):
    """
    重试装饰器（指数退避策略）

    Args:
        max_attempts: 最大尝试次数
        delay: 初始延迟时间（秒）
        backoff: 退避倍数（每次重试延迟 = 上次延迟 * backoff）
        exceptions: 可重试的异常类型元组
        on_retry: 重试回调函数(attempt, exception)

    Example:
        @retry(max_attempts=3, delay=1.0, backoff=2.0)
        async def fetch_data():
            # 可能失败的操作
            return await api_call()

        # 重试流程:
        # 1st attempt: immediate
        # 2nd attempt: wait 1s
        # 3rd attempt: wait 2s (1s * 2)
        # raise exception if all fail
    """

    # 默认可重试的异常
    if exceptions is None:
        exceptions = RetryConfig.RETRYABLE_EXCEPTIONS + RetryConfig.get_db_exceptions()

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    # 尝试执行函数
                    return await func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    # 如果是最后一次尝试，直接抛出异常
                    if attempt == max_attempts:
                        logger.error(
                            f"❌ All {max_attempts} retry attempts failed for {func.__name__}: {e}"
                        )
                        raise

                    # 记录重试日志
                    logger.warning(
                        f"⚠️ Retry attempt {attempt}/{max_attempts} for {func.__name__} "
                        f"after {type(e).__name__}: {e}. "
                        f"Waiting {current_delay:.1f}s..."
                    )

                    # 调用重试回调
                    if on_retry:
                        on_retry(attempt, e)

                    # 等待后重试
                    await asyncio.sleep(current_delay)

                    # 指数退避
                    current_delay *= backoff

                except Exception as e:
                    # 非可重试异常，直接抛出
                    logger.error(
                        f"❌ Non-retryable exception in {func.__name__}: {type(e).__name__}: {e}"
                    )
                    raise

            # 理论上不会执行到这里
            raise last_exception or Exception("Unexpected retry error")

        return wrapper

    return decorator


class CircuitBreaker:
    """
    熔断器模式
    当错误率过高时自动熔断，避免雪崩

    状态机:
    CLOSED → OPEN → HALF_OPEN → CLOSED
       ↑                           ↓
       └───────── (成功) ──────────┘
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception,
    ):
        """
        Args:
            failure_threshold: 失败阈值（连续失败次数）
            recovery_timeout: 恢复超时（秒）
            expected_exception: 预期异常类型
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: float | None = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self, func: Callable, *args, **kwargs):
        """
        通过熔断器调用函数

        Raises:
            Exception: 如果熔断器处于OPEN状态
        """
        import time

        # 检查是否应该尝试恢复
        if self.state == "OPEN":
            if (
                self.last_failure_time
                and time.time() - self.last_failure_time > self.recovery_timeout
            ):
                # 进入半开状态，尝试恢复
                self.state = "HALF_OPEN"
                logger.info(
                    f"Circuit breaker entering HALF_OPEN state for {func.__name__}"
                )
            else:
                raise Exception(
                    f"Circuit breaker is OPEN for {func.__name__}. "
                    f"Please try again later."
                )

        try:
            # 执行函数
            result = await func(*args, **kwargs)

            # 成功执行，重置计数器
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                logger.info(f"✅ Circuit breaker recovered to CLOSED for {func.__name__}")

            self.failure_count = 0
            return result

        except self.expected_exception as e:
            # 记录失败
            self.failure_count += 1
            self.last_failure_time = time.time()

            logger.warning(
                f"Circuit breaker failure {self.failure_count}/{self.failure_threshold} "
                f"for {func.__name__}"
            )

            # 检查是否应该打开熔断器
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.error(
                    f"🔴 Circuit breaker OPENED for {func.__name__} "
                    f"after {self.failure_count} failures"
                )

            raise


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    expected_exception: Type[Exception] = Exception,
):
    """
    熔断器装饰器

    Example:
        @circuit_breaker(failure_threshold=5, recovery_timeout=60)
        async def call_external_api():
            # 可能频繁失败的外部调用
            return await external_service.fetch()
    """
    breaker = CircuitBreaker(failure_threshold, recovery_timeout, expected_exception)

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await breaker.call(func, *args, **kwargs)

        return wrapper

    return decorator


# 组合装饰器示例
def resilient(max_attempts: int = 3, circuit_threshold: int = 5):
    """
    组合重试+熔断器的装饰器

    Example:
        @resilient(max_attempts=3, circuit_threshold=5)
        async def fetch_from_api():
            # 既有重试，又有熔断保护
            return await api.fetch()
    """

    def decorator(func: Callable):
        # 先应用重试，再应用熔断
        func = retry(max_attempts=max_attempts)(func)
        func = circuit_breaker(failure_threshold=circuit_threshold)(func)
        return func

    return decorator
