"""Redis Caching Layer for Daur-AI v2.0"""
import logging
import json
from typing import Optional, Any, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import redis
    from redis import ConnectionPool
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("redis not available")


class RedisCacheConfig:
    def __init__(self, host: str = "localhost", port: int = 6379,
                 db: int = 0, password: Optional[str] = None,
                 max_connections: int = 10):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.max_connections = max_connections


class RedisCache:
    def __init__(self, config: Optional[RedisCacheConfig] = None):
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available. Using in-memory cache")
            self.redis_client = None
            self.memory_cache = {}
            return
        
        self.config = config or RedisCacheConfig()
        try:
            self.pool = ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                max_connections=self.config.max_connections,
                decode_responses=True
            )
            self.redis_client = redis.Redis(connection_pool=self.pool)
            self.redis_client.ping()
            logger.info(f"Redis connected: {self.config.host}:{self.config.port}")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            self.redis_client = None
            self.memory_cache = {}
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            serialized = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
            if self.redis_client:
                if ttl:
                    self.redis_client.setex(key, ttl, serialized)
                else:
                    self.redis_client.set(key, serialized)
            else:
                self.memory_cache[key] = serialized
            return True
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
            else:
                value = self.memory_cache.get(key)
            
            if value is None:
                return None
            
            try:
                return json.loads(value)
            except Exception as e:
                return value
        except Exception as e:
            logger.error(f"Error getting cache: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                self.memory_cache.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"Error deleting cache: {e}")
            return False
    
    def clear(self) -> bool:
        try:
            if self.redis_client:
                self.redis_client.flushdb()
            else:
                self.memory_cache.clear()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        try:
            if self.redis_client:
                return self.redis_client.exists(key) > 0
            else:
                return key in self.memory_cache
        except Exception as e:
            logger.error(f"Error checking cache: {e}")
            return False


class SessionCache:
    def __init__(self, cache: RedisCache, prefix: str = "session:"):
        self.cache = cache
        self.prefix = prefix
    
    def create_session(self, user_id: int, data: Dict, ttl: int = 3600) -> str:
        session_key = f"{self.prefix}{user_id}"
        self.cache.set(session_key, data, ttl=ttl)
        logger.info(f"Session created for user {user_id}")
        return session_key
    
    def get_session(self, user_id: int) -> Optional[Dict]:
        session_key = f"{self.prefix}{user_id}"
        return self.cache.get(session_key)
    
    def delete_session(self, user_id: int):
        session_key = f"{self.prefix}{user_id}"
        self.cache.delete(session_key)
    
    def session_exists(self, user_id: int) -> bool:
        session_key = f"{self.prefix}{user_id}"
        return self.cache.exists(session_key)


class QueryCache:
    def __init__(self, cache: RedisCache, prefix: str = "query:"):
        self.cache = cache
        self.prefix = prefix
    
    def cache_query(self, query: str, result: Any, ttl: int = 300) -> bool:
        cache_key = f"{self.prefix}{hash(query)}"
        return self.cache.set(cache_key, result, ttl=ttl)
    
    def get_cached_query(self, query: str) -> Optional[Any]:
        cache_key = f"{self.prefix}{hash(query)}"
        return self.cache.get(cache_key)


class RateLimitCache:
    def __init__(self, cache: RedisCache, prefix: str = "ratelimit:"):
        self.cache = cache
        self.prefix = prefix
    
    def check_rate_limit(self, identifier: str, max_requests: int, window: int) -> bool:
        key = f"{self.prefix}{identifier}"
        count = self.cache.get(key)
        
        if count is None:
            self.cache.set(key, 1, ttl=window)
            return True
        
        count = int(count) + 1
        
        if count > max_requests:
            return False
        
        self.cache.set(key, count, ttl=window)
        return True
