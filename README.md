# Redis Proxy Server

Access a redis database using a cached proxy server run by Flask and Gunicorn.

## Summary

The purpose of this repository is to play with concurrency and caching in the context of a web app.
The proxy server offers caching abilities on top of a redis database.
Multiple parallel concurrent requests can be made to the cache (see [Architecture](#architecture) for more details).
In particular, the cache evicts the last recently used key given a configurable capacity and keeps keys cached for a configurable expiry time.

To make a query, using the following URL:

```bash
http://{hostname}:{port}/query?key={key_you_are_interested_in}
```

when testing locally, the request:

```bash
http://localhost:5000/query?key=Batman
```

returns `Superhero`.

## Installation and running tests

After cloning this repository with:

```bash
git clone https://github.com/sperez8/redis-proxy-server.git
```

Build the app and run all tests with:
```bash
cd redis-proxy-server
make test
```

### Other commands

Build or rebuild the server and integration test containers:
```bash
make build
```

Build and run only the proxy server (for use in production):
```bash
make run
```

Close the app with:
```bash
make exit
```

### Configurables

All parameters are configurable from the file `.config`. This includes:
- the **Redis backing address hostname and port**: `REDIS_HOST` and `REDIS_PORT`,
- the **IP address**  the proxy server should listen on: `PROXY_LISTEN`,
- the host and container **ports** that will be mapped for the proxy server: `HOST_PORT` and `CONTAINER_PORT`,
- the **cache expiry time**: `CACHE_EXPIRY`
- the **cache capacity** (i.e. number of keys): `CACHE_CAPACITY`

## Architecture

This repo is designed so that the web app can be deployed on its own and without any development dependencies (tests, linting configs, etc.)

The folder structure is as follows:

    .
    ├── proxy                   # all proxy server related files
    │   ├── Dockerfile              # Container for the proxy server
    │   ├── main.py                 # Runs the web app
    │   ├── models.py               # All methods relating to caching/querying the redis database
    │   └── app.py                  # Methods related to the flask app
    ├── test                    # End-to-end tests
    │   ├── Dockerfile              # Container for the integration tests
    │   ├── conftest.py             # pytest fixtures used for setting up a testable redis instance and making server requests
    │   ├── test_cache.py           # All tests associated with configurable cache 
    │   ├── test_concurency.py      # All tests associated with the concurrency of the app
    ├── docker-compose.yml      # Defines services: the proxy server, redis image and integration tests
    ├── .config                 # File where all configurable parameters can be updated
    ├── environment.yml         # Conda environment for proxy server
    ├── environment.dev.yml     # Additional conda dependencies for development and testing only
    ├── Makefile
    └── README.md

The proxy server uses a barebones Flask framework given that it's a simple and lightweight framework. Given specific production requirements, a more sophisticated framework could be used.
The implementation separates the two concerns (app and cache) and thus swapping for a different framework (or a different database) 
should be fairly simple.

The only argument to pass to the app is a method for querying the cache which the function `make_cache()` generates.
Specifically, this method returns a callable function given the cache capacity and expiry parameters using the `cachetools` decorator `TTLCache`.

In the case where a cached key expires, it is not immediately removed from the cache (unless it is evicted by the LRU). From the [documentation](https://cachetools.readthedocs.io/en/latest/#cachetools.TTLCache):

> Items that expire because they have exceeded their time-to-live will be no longer accessible, and will be removed eventually. [...] Expired items will be removed from a cache only at the next mutating operation.

While evicting the key immediately could be implemented, it is assumed the added complexity isn't worth it since we already budgeted for a certain capacity.

### Assumptions
1. Using `cachetools`, a known and widely used open source library, is appropriate for production and tradeoffs convenience for control
2. Given that Redis can accept all sorts of characters in its keys, it is possible that a more rigorous HTTP routing format be necessary to accommodate all possible keys. However this was not the focus of this exercise.
3. Having all configurable parameters (both networking and cache specs) in the same file is convenient. In practice, particularly as more configurable parameters are added, we may want to separate our concerns (networking vs. proxy specs) in different files

## Concurrency Implementation

Multiple parallel concurrent requests can be made to the cache. When a client request is made for a key not already in the cache, a *threading.lock* is used to prevent
all other requests from accessing the cache until this first request is complete. This implementation is to ensure that, given two simultaneous requests for the same key, only one queries the Redis database directly. This way, the number of calls to the database are minimized.

Requests for keys already in the cache do not require the lock, only they wait for the lock to be unlocked if that's not already the case.

Given the desire for even more parallelism, we could instead implement one lock per key in the cache such that all requests to the cache can be processed simultaneously if they are for different keys.

Such an implementation would follow the following pseudocode. First, we would need a means to track all key-lock pairs:

```python
# A dict for all the key-lock pairs
master_lock = {}

# We need a lock for accessing the master_lock
mlock = threading.Lock()
```

When a request is made for key, we add a lock for that key if one doesn't already exist 
```python
with mlock:
    l = master_lock.set_default(k, threading.Lock())
```
Then we use that lock to make our request
```python
with l:
    query_cache(key)
```

Note that this hash map of key-lock pairs could grow quite big though we could easily limit to the size of our cache (for example by defining it within our cache and eliminating key-lock pairs when those keys are evicted from our cache).

While this implementation enables more operations to be run in parallel, it comes at the expense of higher memory usage. 
Given a cache of N keys, the total memory required is O(N) for the cache and O(N) for the key-lock hash for a total of O(2N). 

## Complexity of cache operations

In terms of efficiency, the purpose of a cache is to tradeoff increased memory for faster operations.
The memory of the LRU-TTL cache scales with `O(N)` where `N` is the capacity of the cache set by the user.

Here are the time complexity of different operations:
* Checking if a key is in the cache behaves like a search on a hash map: it takes `O(1)` in the best case, and `O(N)` in the worst case for large caches 
* Adding a new key to the collection of recently used keys takes `O(1)` time since it's akin to adding a pointer to the next item in a linked list
* Looking up a value for a cached key takes `O(1)` time
* Checking the time_to_live of a key takes `O(1)` time
* Scanning for all expired keys and evicting them takes `O(N)` where `N` is the capacity of the cache
* Evicting a key given the LRU capacity takes `O(1)` since the keys are ordered. This operation is equivalent to removing the last item in a linked list

### Possible improvements

* Make tests independent (so they can run in any order and call the same keys)
  * to do so, the cache would need to be cleared between tests (perhaps with a request to a new endpoint to the proxy server) using a *tear_down()* method
* Add the number of allowed clients as a configurable parameter in `.config`
* Add more realistic test data (particularly that test the range of possible key-values accepted by Redis)

### Resources

* https://github.com/Wyntuition/try-python-flask-redis-docker-compose
* https://lucianomolinari.com/2018/05/02/automating-integration-tests-with-docker-compose-and-makefile/
* https://github.com/tkem/cachetools
* https://stackoverflow.com/questions/59931553/how-can-another-python-thread-wait-until-a-lock-is-released
* https://noamkremen.github.io/a-simple-threadsafe-caching-decorator.html
* https://docs.gunicorn.org/en/stable/run.html
