"""Main for the Redis Proxy Server."""
import os
from typing import Callable

from app import create_app
from models import make_cache
from redis import Redis

if __name__ == "__main__":
    # Load all the configurable parameters
    redis_port = os.getenv("REDIS_PORT")
    redis_host = os.getenv("REDIS_HOST")
    proxy_listen = os.getenv("PROXY_LISTEN")
    capacity = int(os.getenv("CACHE_CAPACITY"))
    expiry = int(os.getenv("CACHE_EXPIRY"))
    debug = bool(os.getenv("DEBUG_PROXY"))

    # Connect to redis database
    redis_connection = Redis(host=redis_host, port=redis_port)

    # Build the caching function
    query_cached_redis: Callable = make_cache(
        redis=redis_connection, capacity=capacity, expiry=expiry, debug=debug
    )

    # Create and run flask app
    proxy = create_app(query_func=query_cached_redis)
    proxy.run(host=proxy_listen, debug=debug)
