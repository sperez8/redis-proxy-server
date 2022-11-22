"""All methods related to the Redis instance."""
import time
from typing import Callable

from cachetools import TTLCache, cached
from redis import Redis


def make_cache(
    redis: Redis, capacity: int, expiry: int, debug: bool = True
) -> Callable:
    """Builds the function to call the cache"""

    @cached(cache=TTLCache(maxsize=capacity, ttl=expiry))
    def query_redis(key):
        """An LRU and TTL cached method that queries a redis database."""
        if debug:
            # When debugging, we artificially make the query take a long time to test the cache
            # TODO: this is great for manually testing the cache but we'll eventually remove this
            #  to do something more sophisticated
            time.sleep(2)

        print(f"Querying redis with '{key}'", flush=True)
        return redis.get(key)

    return query_redis


def load_redis(host: str, port: str) -> Redis:
    """Create a redis instance given the desired host address and port."""
    redis = Redis(host=host, port=port)

    # TODO: remove these lines once end-to-end tests set keys in Redis database
    redis.flushdb()
    redis.mset({"Monet": "Painter", "Batman": "Superhero", "Lovecraft": "Writer"})

    return redis
