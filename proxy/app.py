"""All methods related to the flask app."""
import time
from typing import Callable

from flask import Flask, request


def create_app(query_db: Callable, lock):
    """Method for creating the flask app given parameters."""
    app = Flask(__name__)

    @app.route("/")
    def hello_world():
        """Home page."""
        return (
            "Welcome to the Redis Proxy Server. "
            "You can query the redis database using a key with the following URL:   "
            "'hostname:port/query?key={the_key_you_are_interested_in}'"
        )

    @app.route("/query", methods=["GET"])
    def query():
        """Page for querying the cached database using GET methods only."""
        key = request.args.get("key")

        # If the lock is in use, then a new key-value is being set in the cache
        # so we wait for that to be done before we make our query
        while lock.locked():
            time.sleep(0.001)

        return query_db(key)

    return app
