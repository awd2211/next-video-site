"""
API 限流工具
提供细化的限流策略和IP黑名单功能
"""
from typing import Optional, Callable, Dict, List, Any
from fastapi import Request, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
import redis.asyncio as redis
from functools import wraps
from app.config import settings

# 创建限流器实例
limiter = Limiter(key_func=get_remote_address)

# Redis连接(用于IP黑名单)
redis_client = None


async def get_redis_client() -> redis.Redis:
    """获取Redis客户端"""
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
    return redis_client


# 限流策略预设
class RateLimitPresets:
    """限流预设配置"""

    # 严格限流 (写操作/敏感操作)
    STRICT = "5/minute"           # 注册、登录、修改密码
    STRICT_HOUR = "20/hour"       # 每小时20次

    # 中等限流 (搜索/查询)
    MODERATE = "60/minute"        # 搜索、复杂查询
    MODERATE_HOUR = "1000/hour"   # 每小时1000次

    # 宽松限流 (浏览/列表)
    RELAXED = "200/minute"        # 视频列表、分类浏览
    RELAXED_HOUR = "5000/hour"    # 每小时5000次

    # 特殊限流
    UPLOAD = "5/hour"             # 用户上传操作
    COMMENT = "30/minute"         # 评论发布
    SHARE = "50/minute"           # 分享操作
    DOWNLOAD = "10/minute"        # 下载操作

    # 管理员限流 (更宽松)
    ADMIN_WRITE = "100/minute"    # 管理员写操作
    ADMIN_READ = "500/minute"     # 管理员读操作
    # 注意: 管理员上传视频通常不限流


async def check_ip_blacklist(ip: str) -> bool:
    """
    检查IP是否在黑名单中

    Args:
        ip: IP地址

    Returns:
        True if blacklisted, False otherwise
    """
    try:
        client = await get_redis_client()
        result = await client.sismember("ip_blacklist", ip)
        return bool(result)
    except Exception as e:
        print(f"Check IP blacklist error: {e}")
        return False


async def add_to_blacklist(ip: str, reason: str = "", duration: Optional[int] = None) -> None:
    """
    添加IP到黑名单

    Args:
        ip: IP地址
        reason: 封禁原因
        duration: 封禁时长(秒),None表示永久
    """
    try:
        client = await get_redis_client()
        await client.sadd("ip_blacklist", ip)

        # 记录封禁原因和时间
        import time
        await client.hset(f"ip_blacklist_info:{ip}", mapping={
            "reason": reason,
            "banned_at": str(int(time.time())),
        })

        # 如果指定了时长,设置过期时间
        if duration:
            await client.expire(f"ip_blacklist_info:{ip}", duration)
            # 定时移除黑名单
            await client.setex(f"ip_blacklist_temp:{ip}", duration, "1")

    except Exception as e:
        print(f"Add to blacklist error: {e}")


async def remove_from_blacklist(ip: str) -> None:
    """
    从黑名单移除IP

    Args:
        ip: IP地址
    """
    try:
        client = await get_redis_client()
        await client.srem("ip_blacklist", ip)
        await client.delete(f"ip_blacklist_info:{ip}")
        await client.delete(f"ip_blacklist_temp:{ip}")
    except Exception as e:
        print(f"Remove from blacklist error: {e}")


async def get_blacklist() -> List[Dict[str, Any]]:
    """获取所有黑名单IP"""
    try:
        client = await get_redis_client()
        ips: set = await client.smembers("ip_blacklist")

        result: List[Dict[str, Any]] = []
        for ip in ips:
            info: Dict[str, str] = await client.hgetall(f"ip_blacklist_info:{ip}")

            # 检查是否是临时封禁 (存在临时封禁key)
            is_temp: int = await client.exists(f"ip_blacklist_temp:{ip}")

            result.append({
                "ip": str(ip),
                "reason": info.get("reason", ""),
                "banned_at": info.get("banned_at", ""),
                "is_permanent": not bool(is_temp),
            })
        return result
    except Exception as e:
        print(f"Get blacklist error: {e}")
        return []


def check_blacklist_middleware():
    """
    IP黑名单检查中间件装饰器
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取request对象
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if request:
                ip = request.client.host if request.client else None
                if ip and await check_ip_blacklist(ip):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Your IP address has been blocked due to suspicious activity"
                    )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


# 自动封禁检测
class AutoBanDetector:
    """自动封禁检测器"""

    @staticmethod
    async def record_failed_attempt(ip: str, attempt_type: str = "login") -> None:
        """
        记录失败尝试

        Args:
            ip: IP地址
            attempt_type: 尝试类型 (login, register, etc.)
        """
        try:
            client = await get_redis_client()
            key = f"failed_attempts:{attempt_type}:{ip}"

            # 增加计数
            count = await client.incr(key)

            # 设置过期时间 (15分钟)
            if count == 1:
                await client.expire(key, 900)

            # 超过阈值自动封禁
            threshold = 10  # 15分钟内失败10次
            if count >= threshold:
                await add_to_blacklist(
                    ip,
                    reason=f"Too many failed {attempt_type} attempts ({count} times)",
                    duration=3600  # 封禁1小时
                )
                # 清除计数
                await client.delete(key)

        except Exception as e:
            print(f"Record failed attempt error: {e}")

    @staticmethod
    async def clear_failed_attempts(ip: str, attempt_type: str = "login") -> None:
        """清除失败尝试记录"""
        try:
            client = await get_redis_client()
            await client.delete(f"failed_attempts:{attempt_type}:{ip}")
        except Exception as e:
            print(f"Clear failed attempts error: {e}")


# 用户级别限流 (基于用户ID)
def get_user_identifier(request: Request) -> str:
    """
    获取用户标识符(用于用户级限流)
    优先使用user_id,否则使用IP
    """
    # 尝试从请求中获取用户ID
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"

    # 否则使用IP地址
    return f"ip:{get_remote_address(request)}"
