"""Redis caching service"""

import redis.asyncio as redis
import json
import logging
from typing import Optional, Any

from app.config import settings

logger = logging.getLogger(__name__)

_redis_client: Optional[redis.Redis] = None


async def init_redis():
    """Initialize Redis connection"""
    global _redis_client
    try:
        _redis_client = await redis.from_url(settings.REDIS_URL)
        await _redis_client.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Caching disabled.")
        _redis_client = None


async def close_redis():
    """Close Redis connection"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        logger.info("Redis connection closed")


def get_redis() -> Optional[redis.Redis]:
    """Get Redis client instance"""
    return _redis_client


async def cache_get(key: str) -> Optional[Any]:
    """Get value from cache"""
    try:
        client = get_redis()
        if not client:
            return None
        
        value = await client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.warning(f"Cache get failed: {e}")
        return None


async def cache_set(key: str, value: Any, expiry: Optional[int] = None):
    """Set value in cache"""
    try:
        client = get_redis()
        if not client:
            return
        
        expiry = expiry or settings.REDIS_CACHE_EXPIRY
        await client.setex(
            key,
            expiry,
            json.dumps(value, default=str)
        )
    except Exception as e:
        logger.warning(f"Cache set failed: {e}")


async def cache_delete(key: str):
    """Delete value from cache"""
    try:
        client = get_redis()
        if not client:
            return
        
        await client.delete(key)
    except Exception as e:
        logger.warning(f"Cache delete failed: {e}")


async def cache_clear():
    """Clear all cache"""
    try:
        client = get_redis()
        if not client:
            return
        
        await client.flushdb()
        logger.info("Cache cleared")
    except Exception as e:
        logger.warning(f"Cache clear failed: {e}")
