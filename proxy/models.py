"""All methods related to the Redis instance."""
from typing import Callable

from cachetools import TTLCache, cached
from redis import Redis


def make_cache(redis: Redis, capacity: int, expiry: int) -> Callable:
    """Builds the function to call the cache"""

    @cached(cache=TTLCache(maxsize=capacity, ttl=expiry))
    def query_redis(key):
        """An LRU and TTL cached method that queries a redis database."""
        return redis.get(key)

    return query_redis
