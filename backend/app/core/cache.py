"""
TenderWise AI - Redis Caching Service
High-performance caching for API responses and data
"""
import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta
import logging
import os

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CacheService:
    """
    High-performance caching service with Redis backend
    Falls back to in-memory cache if Redis unavailable
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = None
        self.memory_cache = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
        
        # Try to connect to Redis
        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.from_url(
                    redis_url, 
                    decode_responses=False,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Connected to Redis cache")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Using memory cache.")
                self.redis_client = None
        else:
            logger.info("Redis not available. Using in-memory cache.")
    
    def _serialize_key(self, key: str) -> str:
        """Ensure key is properly formatted for Redis"""
        return f"tenderwise:{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for storage"""
        if isinstance(value, (str, int, float, bool)):
            return json.dumps(value).encode('utf-8')
        else:
            return pickle.dumps(value)
    
    def _deserialize_value(self, value: bytes) -> Any:
        """Deserialize value from storage"""
        try:
            # Try JSON first (faster)
            return json.loads(value.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle
            return pickle.loads(value)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.redis_client:
                # Redis cache
                serialized_key = self._serialize_key(key)
                value = self.redis_client.get(serialized_key)
                if value is not None:
                    self.cache_stats["hits"] += 1
                    return self._deserialize_value(value)
            else:
                # Memory cache
                if key in self.memory_cache:
                    entry = self.memory_cache[key]
                    # Check expiration
                    if entry.get("expires_at") and entry["expires_at"] < time.time():
                        del self.memory_cache[key]
                        self.cache_stats["misses"] += 1
                        return None
                    self.cache_stats["hits"] += 1
                    return entry["value"]
            
            self.cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.cache_stats["misses"] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL (seconds)"""
        try:
            if self.redis_client:
                # Redis cache
                serialized_key = self._serialize_key(key)
                serialized_value = self._serialize_value(value)
                
                if ttl:
                    self.redis_client.setex(serialized_key, ttl, serialized_value)
                else:
                    self.redis_client.set(serialized_key, serialized_value)
            else:
                # Memory cache
                import time
                entry = {
                    "value": value,
                    "created_at": time.time()
                }
                if ttl:
                    entry["expires_at"] = time.time() + ttl
                self.memory_cache[key] = entry
            
            self.cache_stats["sets"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if self.redis_client:
                # Redis cache
                serialized_key = self._serialize_key(key)
                result = self.redis_client.delete(serialized_key)
                self.cache_stats["deletes"] += 1
                return result > 0
            else:
                # Memory cache
                if key in self.memory_cache:
                    del self.memory_cache[key]
                    self.cache_stats["deletes"] += 1
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def clear(self, pattern: Optional[str] = None) -> bool:
        """Clear cache entries (optionally by pattern)"""
        try:
            if self.redis_client:
                if pattern:
                    keys = self.redis_client.keys(self._serialize_key(pattern))
                    if keys:
                        self.redis_client.delete(*keys)
                else:
                    self.redis_client.flushdb()
            else:
                if pattern:
                    # Simple pattern matching for memory cache
                    keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
                    for key in keys_to_delete:
                        del self.memory_cache[key]
                else:
                    self.memory_cache.clear()
            
            return True
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get cache performance statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        stats = {
            **self.cache_stats,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2),
            "backend": "redis" if self.redis_client else "memory",
            "memory_cache_size": len(self.memory_cache) if not self.redis_client else None
        }
        
        return stats
    
    def is_healthy(self) -> bool:
        """Check if cache service is healthy"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
            else:
                # Memory cache is always "healthy"
                return True
        except Exception:
            return False


# Global cache instance
cache_service = CacheService(
    redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)


# Convenience functions
async def get_cached(key: str) -> Optional[Any]:
    """Get value from cache"""
    return await cache_service.get(key)


async def set_cached(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Set value in cache"""
    return await cache_service.set(key, value, ttl)


async def delete_cached(key: str) -> bool:
    """Delete value from cache"""
    return await cache_service.delete(key)


async def clear_cache(pattern: Optional[str] = None) -> bool:
    """Clear cache"""
    return await cache_service.clear(pattern)


# Cache decorators
def cache_response(ttl: int = 300, key_prefix: str = "api"):
    """
    Decorator to cache API responses
    
    Args:
        ttl: Time to live in seconds (default 5 minutes)
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            import hashlib
            key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            cache_key = f"{key_prefix}:{hashlib.md5(key_data.encode()).hexdigest()}"
            
            # Try to get from cache
            cached_result = await get_cached(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            await set_cached(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


import asyncio