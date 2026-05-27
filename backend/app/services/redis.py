"""Redis async connection pool for the VFS application."""
import logging
from typing import Optional
from redis import asyncio as aioredis
from app.config import get_settings

logger = logging.getLogger(__name__)

_pool: Optional[aioredis.ConnectionPool] = None


async def get_redis() -> aioredis.Redis:
    """Get a Redis connection from the shared pool (singleton)."""
    global _pool
    if _pool is None:
        settings = get_settings()
        _pool = aioredis.ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=10,
            decode_responses=True,
        )
        logger.info("Redis connection pool created")
    return aioredis.Redis(connection_pool=_pool)


async def close_redis() -> None:
    """Close the Redis connection pool (call on shutdown)."""
    global _pool
    if _pool is not None:
        await _pool.disconnect()
        _pool = None
        logger.info("Redis connection pool closed")
