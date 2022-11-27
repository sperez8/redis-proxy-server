"""Integration tests for the concurrent access to the proxy cache."""
import concurrent.futures

import requests


def test_many_concurrent_requests_same_key(redis, proxy_home, data):
    """When two requests are made to the same key, the cache is used for one of the requests."""

    # Let's call the same key concurrently many times
    keys = ["Fiona Staples"] * 20 + ["Clara Hughes"] * 20
    urls = [f"{proxy_home}/query?key={key}" for key in keys]

    hits_before = redis.info()["keyspace_hits"]

    values = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # we can't pass nested functions to the Concurrent Executor (since they can't be pickled)
        # see: https://docs.python.org/3/library/concurrent.futures.html#processpoolexecutor
        # so we pass request.get() function call directly instead of the fixture 'proxy_get()'
        for response in executor.map(requests.get, urls):
            values.append(response.text)

    hits_after = redis.info()["keyspace_hits"]

    # If our cache is thread-safe, only two requests would have been made to Redis
    # (one per unique key) and other processes would have waited for access to the cache
    assert hits_after - hits_before == 2

    # Let's check the values
    assert set(values) == {data[k] for k in keys}
