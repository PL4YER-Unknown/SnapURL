import redis
from flask import current_app

redis_client = None


def init_redis(app):
    """
    Initialize the Redis client.
    Called at Flask startup from __init__.py
    """
    global redis_client

    # Use app.config instead of current_app.config
    redis_client = redis.Redis(
        host=app.config["REDIS_HOST"],
        port=app.config["REDIS_PORT"],
        db=0,
        decode_responses=True
    )
    # global redis_client
    # config = current_app.config

    # redis_client = redis.Redis(
    #     host=config["REDIS_HOST"],
    #     port=config["REDIS_PORT"],
    #     decode_responses=True,
    # )


# ------------------------------
#          CACHE OPS
# ------------------------------

CACHE_PREFIX = "URL:"


def cache_get(short_code: str):
    """
    Retrieve long URL from Redis cache.
    """
    key = f"{CACHE_PREFIX}{short_code}"
    return redis_client.get(key)


def cache_set(short_code: str, long_url: str, ttl_seconds=86400):
    """
    Store long URL in Redis with optional TTL (default: 24 hours).
    """
    key = f"{CACHE_PREFIX}{short_code}"
    redis_client.set(key, long_url, ex=ttl_seconds)


def cache_delete(short_code: str):
    """
    Remove entry from cache (if needed).
    """
    key = f"{CACHE_PREFIX}{short_code}"
    redis_client.delete(key)
