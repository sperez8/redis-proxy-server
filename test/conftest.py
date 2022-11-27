"""All pytest fixtures."""
import os

import pytest
import requests
from redis import Redis


@pytest.fixture(scope="session", autouse=True)
def data():
    """The key-value pairs we want to insert into the redis database."""
    return {
        "Monet": "Painter",
        "Batman": "Superhero",
        "Lovecraft": "Writer",
        "Lovelace": "Programmer",
        "Banksy": "Unknown",
        "Clara Hughes": "Olympian",
        "Fiona Staples": "Comic Artist",
    }


@pytest.fixture(scope="session")
def capacity(data):
    """The LRU capacity of the proxy server's cache."""
    capicity = int(os.getenv("CACHE_CAPACITY"))

    # For our tests to work, we need more keys than the cache capacity
    assert len(data) > capicity, (
        "The test dataset has too few keys. "
        "Either decrease the proxy cache's test capacity or add more keys."
    )

    return capicity


@pytest.fixture(scope="session")
def expiry():
    """The TTL expiry of the proxy server's cache."""
    expiry = int(os.getenv("CACHE_EXPIRY"))

    # We don't want our test to take to long so the expiry time should be short
    assert expiry < 5  # seconds

    return expiry


@pytest.fixture(scope="session", autouse=True)
def redis(data):
    """Define the fixture for the redis instance and fill it with test data."""
    # Connect to the redis instance
    redis_port = os.getenv("REDIS_PORT")
    redis_host = os.getenv("REDIS_HOST")
    redis = Redis(host=redis_host, port=redis_port)

    # Add test data
    redis.flushdb()
    redis.mset(data)

    # Let's check that the number of keys in redis is the same as we put in
    assert redis.info()["db0"]["keys"] == len(data)

    return redis


@pytest.fixture(scope="session")
def proxy_home():
    """Address of the proxy server."""
    proxy_listen = "proxy"  # this is the name of the docker-compose service
    proxy_port = os.getenv("PROXY_PORT")
    proxy_address = f"http://{proxy_listen}:{proxy_port}/"

    # let's check we can connect to it before running our tests
    r = requests.get(proxy_address)
    assert r.status_code == 200

    return proxy_address


@pytest.fixture(scope="session")
def proxy_get(proxy_home):
    """Creates proxy GET function."""

    def get(key):
        """Request function to make an HTTP GET to the proxy server"""
        response = requests.get(f"{proxy_home}/query?key={key}")
        assert response.status_code == 200
        return response.text

    return get
