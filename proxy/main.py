"""Main for the Redis Proxy Server."""
import os
from typing import Callable

from app import create_app
from models import load_redis, make_cache
from redis import Redis

if __name__ == "__main__":
    # Load all the configurable parameters
    redis_port = os.getenv("REDIS_PORT")
    redis_host = os.getenv("REDIS_HOST")
    proxy_listen = os.getenv("PROXY_LISTEN")
    capacity = int(os.getenv("CACHE_CAPACITY"))
    expiry = int(os.getenv("CACHE_EXPIRY"))
    print(redis_port, redis_host, proxy_listen, capacity, expiry)

    # Connect to redis database and fill it
    # TODO: only connect to redis here. Fill redis in tests, not web app
    redis_connection: Redis = load_redis(host=redis_host, port=redis_port)

    # Build the caching function
    query_cached_redis: Callable = make_cache(
        redis=redis_connection, capacity=capacity, expiry=expiry, debug=True
    )

    # Create and run flask app
    proxy = create_app(query_func=query_cached_redis)
    proxy.run(host=proxy_listen, debug=True)
