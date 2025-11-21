from flask import Flask
from .api import api_bp
from .config import Config
from .db import init_db_pools
from .cache import init_redis


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Redis cache
    init_redis(app)

    # Initialize DB shard pools
    init_db_pools(app)

    # Register API routes
    app.register_blueprint(api_bp)

    return app
# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)

#     # init modules
#     init_db_pools(app)
#     init_redis(app)

#     # register routes
#     from app.routes import url_bp
#     app.register_blueprint(url_bp)

#     return app