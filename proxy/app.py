"""All methods related to the flask app."""
from typing import Callable

from flask import Flask, request


def create_app(query_func: Callable, lock):
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
        """Page for querying the cached redis database using GET methods only."""
        key = request.args.get("key")
        with lock:
            return query_func(key)

    return app
