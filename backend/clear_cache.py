#!/usr/bin/env python3
"""
清除缓存脚本
用于解决缓存导致的API 500错误
"""
import asyncio
from app.utils.cache import get_redis


async def clear_cache():
    """清除所有或特定模式的缓存"""
    print("连接到Redis...")
    redis = await get_redis()

    # 清除特定模式的keys
    patterns = [
        "categories:*",
        "countries:*",
        "tags:*",
        "videos:featured:*",
        "videos:recommended:*",
        "recommendations:*",
    ]

    total_cleared = 0

    for pattern in patterns:
        keys = await redis.keys(pattern)
        if keys:
            await redis.delete(*keys)
            print(f"✓ 清除 {len(keys)} 个keys匹配 '{pattern}'")
            total_cleared += len(keys)
        else:
            print(f"  没有keys匹配 '{pattern}'")

    await redis.aclose()
    print(f"\n总共清除 {total_cleared} 个缓存keys")
    print("缓存清理完成!")


if __name__ == "__main__":
    asyncio.run(clear_cache())
