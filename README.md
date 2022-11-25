# Redis Proxy Server

Access a redis database using a cached proxy server implemented using Flask.

## Summary

The purpose of this repository is to play with concurrency and caching in the context of a web app.
The proxy server offers caching abilities on top of a redis database. 
In particular the cache evicts the last recently used key given a configurable capacity and keeps keys cached for a configurable expiry time.

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

## Other commands

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

## Configurable options

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
    ├── docker-compose.yml      # Defines services: the proxy server, redis image and integration tests
    ├── .config                 # File where all configurable parameters can be updated
    ├── environment.yml         # Conda environment for proxy server
    ├── environment.dev.yml     # Additional conda dependencies for development and testing only
    ├── Makefile
    └── README.md

The proxy server uses a barebones Flask app given that it's a simple and lightweight framework. Given specific production requirements, a more sophisticated framework could be used.
The implementation separates the two concerns (app and cache) and thus swapping for a different framework should be fairly simple.

**TBD**: It is possible that using Flask will hamper the task of limiting the number concurrent clients.

The only argument to pass to the app is a method for querying the cache which the function `make_cache()` generates.
Specifically, this method returns a callable function given the cache capacity and expiry parameters using the `cachetools` decorator `TTLCache`.

In the case where a cached key expires, it is not immediately removed from the cache (unless it is evicted by the LRU). From the [documentation](https://cachetools.readthedocs.io/en/latest/#cachetools.TTLCache):

> Items that expire because they have exceeded their time-to-live will be no longer accessible, and will be removed eventually. [...] Expired items will be removed from a cache only at the next mutating operation.

While evicting the key immediately could be implemented, it is assumed the added complexity isn't worth it since we already budgeted for a certain capacity.

**TBD**: It is possible that using the `cachetools` decorator will hamper any concurrency we want to implement.
In fact the documentation specifically mentions that the library is not threadsafe.

### Assumptions
1. Using `cachetools`, a known and widely used open source library, is appropriate for production and tradeoffs convenience for control
2. Given that Redis can accept all sorts of characters in its keys, it is possible that a more rigorous HTTP routing format be necessary to accommodate all possible keys. Since this wasn't the focus app the assignment, I did not spend time testing this implementation decision
3. Having all configurable parameters (both networking and cache specs) in the same file is convenient. In practice, particularly as more configurable parameters are added, we may want to separate our concerns (networking vs. proxy specs) in different files

## Complexity of cache operations

The sole purpose of a cache is to tradeoff heavy memory usage for faster operations.
The memory of the LRU-TTL cache scales with `O(N)` where `N` is the capacity of the cache set by the user.

Here are the time complexity of different operations:
* Checking if a key is in the cache behaves like a search on a hash map: it takes `O(1)` in the best case, and `O(N)` in the worst case for large caches 
* Adding a key to the collection of recently used keys takes `O(1)` since it's akin to adding a pointer to the next item in a linked list
* Accessing a value for a cached key `O(1)` 
* Checking the time_to_live of a key takes `O(1)`
* Scanning for all expired keys and evicting them takes `O(N)` where `N` is the capacity of the cache
* Evicting a key given the LRU capacity takes `O(1)` since the keys are ordered. This operation is equivalent to removing the last item in a linked list

## In progress

Here are the next steps:

* Make tests independent (so they can run in any order and in parallel)
  * to do so, ideally the integration tests can make a call to the proxy server to clear the cache between tests
* Implement parallel concurrent processing with multiple clients
* Add number of allowed clients as a configurable parameter in `.config`

