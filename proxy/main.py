"""Main for the Redis Proxy Server."""
import os

from app import create_app
from models import load_redis

if __name__ == "__main__":
    # Load all the configurable parameters
    redis_port = os.getenv("REDIS_PORT")
    redis_host = os.getenv("REDIS_HOST")
    proxy_listen = os.getenv("PROXY_LISTEN")
    capacity = os.getenv("CACHE_CAPACITY")
    expiry = os.getenv("CACHE_EXPIRY")
    print(redis_port, redis_host, proxy_listen)

    # Connect to redis database and fill it
    # TODO: fill redis in tests, not web app
    redis_instance = load_redis(host=redis_host, port=redis_port)

    # Create and run flask app
    proxy = create_app(redis=redis_instance)
    proxy.run(host=proxy_listen, debug=True)
