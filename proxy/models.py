"""All methods related to the Redis instance."""
from redis import Redis


def load_redis(host: str, port: str):
    """Create a redis instance given the desired host address and port."""
    redis = Redis(host=host, port=port)

    redis.flushdb()
    redis.mset({"Monet": "Painter", "Batman": "Superhero"})

    return redis
