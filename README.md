# Redis Proxy Server

Access a redis database using a proxy server.

## Summary

**FILL ME**

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

Build or rebuild the app:
```bash
make build
```

Run just the proxy server:
```bash
make run
```

Close the app with:
```bash
make exit
```

## Configurable options

All parameters are configurable from the file `.config`. This includes:
- the **Redis backing address host and port**: `REDIS_HOST` and `REDIS_PORT`,
- the **IP address**  the proxy server should listen on: `PROXY_LISTEN`,
- the host and container **ports** that will be mapped for the proxy server: `HOST_PORT` and `CONTAINER_PORT`,
- the **cache expiry time**: `CACHE_EXPIRY`
- the **cache capacity** (number of keys): `CACHE_CAPACITY`

## Architecture

**FILL ME**

## Big O complexity of cache operations

**FILL ME**