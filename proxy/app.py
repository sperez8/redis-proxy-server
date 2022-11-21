"""All methods related to the flask app."""

from flask import Flask, request


def create_app(redis):
    """Method for creating the flask app given parameters."""
    app = Flask(__name__)

    @app.route("/")
    def hello_world():
        """Home page."""
        return (
            "Welcome to the Redis Proxy Server. "
            "You can query the redis database using a key using an URL in the form of: "
            "'home/query?key={the_key_you_are_interested_in}'"
        )

    @app.route("/query")
    def query():
        """Page for querying the redis database using GET methods only."""
        key = request.args.get("key")
        return redis.get(key)

    return app
