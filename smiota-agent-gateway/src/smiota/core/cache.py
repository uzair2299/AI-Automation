"""Asynchronous Redis Cache & Distributed State Manager with In-Memory Fallback."""
import json
from typing import Any, Optional
import redis.asyncio as aioredis
from redis.asyncio.connection import ConnectionPool

from smiota.core.config import get_settings
from smiota.core.logging import logger

_pool: Optional[ConnectionPool] = None
_client: Optional[aioredis.Redis] = None
_initialized: bool = False
_memory_cache: dict[str, Any] = {}


class CacheService:
    """Async Redis cache service with automatic serialization and fast in-memory fallback."""

    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        self.client = redis_client

    @classmethod
    async def initialize(cls) -> "CacheService":
        """Initialize connection pool to Redis or switch to in-memory mode."""
        global _pool, _client, _initialized
        _initialized = True
        settings = get_settings()
        try:
            _pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=20,
                decode_responses=True,
                socket_connect_timeout=0.3,
                socket_timeout=0.3,
            )
            _client = aioredis.Redis(connection_pool=_pool)
            await _client.ping()
            logger.info("Connected to Redis cache successfully.")
            return cls(_client)
        except Exception as e:
            logger.info(f"Redis not detected locally, operating in fast in-memory cache mode.")
            _client = None
            return cls(None)

    async def get(self, key: str) -> Optional[Any]:
        """Fetch value from Redis or in-memory cache."""
        if not self.client:
            return _memory_cache.get(key)
        try:
            val = await self.client.get(key)
            return json.loads(val) if val else None
        except Exception:
            return _memory_cache.get(key)

    async def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """Store value in Redis or in-memory cache."""
        _memory_cache[key] = value
        if not self.client:
            return True
        try:
            serialized = json.dumps(value, default=str)
            await self.client.set(key, serialized, ex=ttl_seconds)
            return True
        except Exception:
            return True

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        _memory_cache.pop(key, None)
        if not self.client:
            return True
        try:
            await self.client.delete(key)
            return True
        except Exception:
            return True

    async def is_healthy(self) -> bool:
        """Check if cache connection is active."""
        if not self.client:
            return True  # In-memory cache is always healthy
        try:
            return await self.client.ping()
        except Exception:
            return False


async def get_cache_service() -> CacheService:
    """Dependency for injecting cache service."""
    global _client, _initialized
    if not _initialized:
        return await CacheService.initialize()
    return CacheService(_client)


async def close_cache() -> None:
    """Close Redis client pool."""
    global _client, _pool, _initialized
    if _client:
        await _client.close()
        _client = None
    if _pool:
        await _pool.disconnect()
        _pool = None
    _initialized = False
