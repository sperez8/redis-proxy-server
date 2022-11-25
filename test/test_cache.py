"""Integration tests for the TTL and LRU properties of the proxy cache."""

import time


def test_cached_key(redis, proxy_get, data):
    """
    Test that a new key elicits a hit in redis
    but that requesting that key again uses the cache (and doesn't hit redis again)
    """
    key = "Lovelace"

    hits_before = redis.info()["keyspace_hits"]
    value = proxy_get(key)
    hits_after = redis.info()["keyspace_hits"]

    # We should have made one GET to Redis
    assert hits_before + 1 == hits_after
    assert value == data[key]

    # Now if we request the key again
    cached_value = proxy_get(key)
    hits_after_again = redis.info()["keyspace_hits"]

    # We should get no new redis hits
    assert hits_after == hits_after_again
    assert cached_value == value


def test_expiry_eviction(redis, proxy_get, expiry):
    """
    Test the cache's TTL feature.
    And that after eviction, the key can be recached.
    """
    key = "Batman"
    proxy_get(key)
    hits_before = redis.info()["keyspace_hits"]

    # We wait as long as the expiry and query the proxy again
    time.sleep(expiry)
    proxy_get(key)
    hits_after = redis.info()["keyspace_hits"]

    # We should have another GET to Redis since the key was evicted
    assert hits_before + 1 == hits_after

    # But its TTL is updated and it is back in the cache now
    hits_before2 = redis.info()["keyspace_hits"]
    proxy_get(key)
    hits_after2 = redis.info()["keyspace_hits"]
    assert hits_before2 == hits_after2


def test_capacity_eviction(redis, proxy_get, data, capacity):
    """
    Test the cache's LRU feature.
    And that after eviction, the key can be recached.
    """
    keys = list(data.keys())

    # We request keys until we make as many requests as the capacity + 1
    for i, k in enumerate(keys):
        if i == capacity + 1:
            break
        proxy_get(k)

    # We request the first key again which should have been evicted
    evicted_key = keys[0]
    hits_before = redis.info()["keyspace_hits"]
    proxy_get(evicted_key)
    hits_after = redis.info()["keyspace_hits"]

    # We should have made one GET to Redis since it was evicted from the cache
    assert hits_before + 1 == hits_after

    # But it is back at the top of the LRU cache now
    hits_before2 = redis.info()["keyspace_hits"]
    proxy_get(evicted_key)
    hits_after2 = redis.info()["keyspace_hits"]
    assert hits_before2 == hits_after2
