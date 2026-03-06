"""
Cache utilities using Redis
"""
import json
import pickle
from typing import Optional, Any, Union
from datetime import timedelta

import redis.asyncio as redis

from app.config import get_settings

settings = get_settings()


class Cache:
    """Redis cache wrapper"""
    
    _instance = None
    _redis = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self):
        """Connect to Redis"""
        if self._redis is None:
            self._redis = await redis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                encoding="utf-8",
                decode_responses=True
            )
        return self._redis
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self._redis:
            await self._redis.close()
            self._redis = None
    
    async def get(self, key: str) -> Optional[str]:
        """Get string value from cache"""
        r = await self.connect()
        return await r.get(key)
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value from cache"""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(
        self,
        key: str,
        value: Union[str, bytes],
        ttl: Optional[int] = None
    ):
        """Set value in cache"""
        r = await self.connect()
        if ttl:
            await r.setex(key, ttl, value)
        else:
            await r.set(key, value)
    
    async def set_json(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ):
        """Set JSON value in cache"""
        await self.set(key, json.dumps(value), ttl)
    
    async def delete(self, key: str):
        """Delete key from cache"""
        r = await self.connect()
        await r.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        r = await self.connect()
        return await r.exists(key) > 0
    
    async def expire(self, key: str, seconds: int):
        """Set expiration for key"""
        r = await self.connect()
        await r.expire(key, seconds)
    
    async def ttl(self, key: str) -> int:
        """Get remaining TTL for key"""
        r = await self.connect()
        return await r.ttl(key)
    
    # Hash operations
    async def hget(self, key: str, field: str) -> Optional[str]:
        """Get hash field value"""
        r = await self.connect()
        return await r.hget(key, field)
    
    async def hgetall(self, key: str) -> dict:
        """Get all hash fields"""
        r = await self.connect()
        return await r.hgetall(key)
    
    async def hset(self, key: str, field: str, value: str):
        """Set hash field value"""
        r = await self.connect()
        await r.hset(key, field, value)
    
    async def hdel(self, key: str, field: str):
        """Delete hash field"""
        r = await self.connect()
        await r.hdel(key, field)
    
    # List operations
    async def lpush(self, key: str, value: str):
        """Push to list head"""
        r = await self.connect()
        await r.lpush(key, value)
    
    async def rpush(self, key: str, value: str):
        """Push to list tail"""
        r = await self.connect()
        await r.rpush(key, value)
    
    async def lpop(self, key: str) -> Optional[str]:
        """Pop from list head"""
        r = await self.connect()
        return await r.lpop(key)
    
    async def rpop(self, key: str) -> Optional[str]:
        """Pop from list tail"""
        r = await self.connect()
        return await r.rpop(key)
    
    async def lrange(self, key: str, start: int, end: int) -> list:
        """Get list range"""
        r = await self.connect()
        return await r.lrange(key, start, end)
    
    # Set operations
    async def sadd(self, key: str, member: str):
        """Add to set"""
        r = await self.connect()
        await r.sadd(key, member)
    
    async def srem(self, key: str, member: str):
        """Remove from set"""
        r = await self.connect()
        await r.srem(key, member)
    
    async def smembers(self, key: str) -> set:
        """Get set members"""
        r = await self.connect()
        return await r.smembers(key)
    
    async def sismember(self, key: str, member: str) -> bool:
        """Check if member in set"""
        r = await self.connect()
        return await r.sismember(key, member)
    
    # Sorted set operations
    async def zadd(self, key: str, mapping: dict):
        """Add to sorted set"""
        r = await self.connect()
        await r.zadd(key, mapping)
    
    async def zrange(
        self,
        key: str,
        start: int,
        end: int,
        withscores: bool = False
    ) -> list:
        """Get sorted set range"""
        r = await self.connect()
        return await r.zrange(key, start, end, withscores=withscores)
    
    async def zrevrange(
        self,
        key: str,
        start: int,
        end: int,
        withscores: bool = False
    ) -> list:
        """Get sorted set reverse range"""
        r = await self.connect()
        return await r.zrevrange(key, start, end, withscores=withscores)
    
    async def zrem(self, key: str, member: str):
        """Remove from sorted set"""
        r = await self.connect()
        await r.zrem(key, member)
    
    # Pub/Sub operations
    async def publish(self, channel: str, message: str):
        """Publish message to channel"""
        r = await self.connect()
        await r.publish(channel, message)
    
    # Key patterns
    async def keys(self, pattern: str) -> list:
        """Get keys matching pattern"""
        r = await self.connect()
        return await r.keys(pattern)
    
    async def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern"""
        r = await self.connect()
        keys = await r.keys(pattern)
        if keys:
            await r.delete(*keys)


# Global cache instance
cache = Cache()


# Helper functions for common use cases

async def get_market_snapshot(symbol: str) -> Optional[dict]:
    """Get market snapshot from cache"""
    return await cache.get_json(f"market:snapshot:{symbol}")


async def set_market_snapshot(symbol: str, data: dict, ttl: int = 5):
    """Set market snapshot in cache"""
    await cache.set_json(f"market:snapshot:{symbol}", data, ttl)


async def get_symbol_detail(symbol: str) -> Optional[dict]:
    """Get symbol detail from cache"""
    return await cache.get_json(f"market:detail:{symbol}")


async def set_symbol_detail(symbol: str, data: dict, ttl: int = 10):
    """Set symbol detail in cache"""
    await cache.set_json(f"market:detail:{symbol}", data, ttl)


async def get_user_session(user_id: int) -> Optional[dict]:
    """Get user session from cache"""
    return await cache.get_json(f"user:session:{user_id}")


async def set_user_session(user_id: int, data: dict, ttl: int = 3600):
    """Set user session in cache"""
    await cache.set_json(f"user:session:{user_id}", data, ttl)


async def delete_user_session(user_id: int):
    """Delete user session from cache"""
    await cache.delete(f"user:session:{user_id}")


async def get_rate_limit_key(key: str) -> Optional[str]:
    """Get rate limit counter"""
    return await cache.get(f"rate_limit:{key}")


async def increment_rate_limit(key: str, window: int = 60) -> int:
    """Increment rate limit counter"""
    r = await cache.connect()
    current = await r.incr(f"rate_limit:{key}")
    if current == 1:
        await r.expire(f"rate_limit:{key}", window)
    return current
