"""
JWT Token黑名单管理
用于实现Token撤销功能（登出、密码修改、权限变更等场景）
"""

import hashlib
import json
from datetime import datetime
from typing import Optional

import redis.asyncio as redis
from loguru import logger

from app.config import settings


async def get_redis_client() -> redis.Redis:
    """获取Redis客户端"""
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
    )


def get_token_hash(token: str) -> str:
    """
    获取token的哈希值（用于存储）
    避免在Redis中存储完整token

    Args:
        token: JWT token

    Returns:
        SHA256哈希值
    """
    return hashlib.sha256(token.encode()).hexdigest()


async def add_to_blacklist(
    token: str, reason: str = "logout", expires_in: Optional[int] = None
) -> bool:
    """
    将token添加到黑名单

    Args:
        token: JWT token
        reason: 撤销原因 (logout, password_change, permission_revoked等)
        expires_in: 过期时间（秒），None则使用token自身的过期时间

    Returns:
        是否成功
    """
    try:
        client = await get_redis_client()
        token_hash = get_token_hash(token)

        # 如果没有指定过期时间，使用默认值（refresh token的过期时间）
        if expires_in is None:
            expires_in = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600

        # 存储到Redis，带过期时间
        key = f"token_blacklist:{token_hash}"
        await client.setex(
            key,
            expires_in,
            json.dumps(
                {"reason": reason, "blacklisted_at": datetime.now().isoformat()}
            ),
        )

        return True
    except Exception as e:
        logger.error(f"Add to token blacklist error: {e}", exc_info=True)
        return False


async def is_blacklisted(token: str) -> bool:
    """
    检查token是否在黑名单中

    Args:
        token: JWT token

    Returns:
        是否在黑名单中
    """
    try:
        client = await get_redis_client()
        token_hash = get_token_hash(token)
        key = f"token_blacklist:{token_hash}"

        exists = await client.exists(key)
        return exists > 0
    except Exception as e:
        logger.error(f"Check token blacklist error: {e}", exc_info=True)
        # 安全起见，如果Redis出错，拒绝token
        return True


async def remove_from_blacklist(token: str) -> bool:
    """
    从黑名单移除token（一般不需要，因为会自动过期）

    Args:
        token: JWT token

    Returns:
        是否成功
    """
    try:
        client = await get_redis_client()
        token_hash = get_token_hash(token)
        key = f"token_blacklist:{token_hash}"

        await client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Remove from token blacklist error: {e}", exc_info=True)
        return False


async def revoke_all_user_tokens(user_id: int) -> bool:
    """
    撤销用户的所有token
    通过记录用户的token版本号实现

    Args:
        user_id: 用户ID

    Returns:
        是否成功
    """
    try:
        client = await get_redis_client()
        key = f"user_token_version:{user_id}"

        # 增加版本号
        await client.incr(key)

        # 设置过期时间（refresh token的过期时间）
        await client.expire(key, settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600)

        return True
    except Exception as e:
        logger.error(f"Revoke all user tokens error: {e}", exc_info=True)
        return False


async def get_user_token_version(user_id: int) -> int:
    """
    获取用户的token版本号

    Args:
        user_id: 用户ID

    Returns:
        版本号（默认为0）
    """
    try:
        client = await get_redis_client()
        key = f"user_token_version:{user_id}"

        version = await client.get(key)
        return int(version) if version else 0
    except Exception as e:
        logger.error(f"Get user token version error: {e}", exc_info=True)
        return 0
