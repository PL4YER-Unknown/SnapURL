import time
from flask import request
from .cache import redis_client


def get_client_id():
    """
    Identify the client making the request.
    Options:
    - IP address (default)
    - Could be extended to API keys
    """
    return request.remote_addr


def rate_limit(max_requests: int, window_seconds: int):
    """
    Sliding window rate limiter decorator.
    Example: @rate_limit(20, 60) => 20 requests per 60 seconds
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            client_id = get_client_id()
            now = int(time.time())

            key = f"RL:{client_id}"

            # Remove entries older than sliding window
            redis_client.zremrangebyscore(key, 0, now - window_seconds)

            # Count entries in the window
            current_count = redis_client.zcard(key)

            if current_count >= max_requests:
                return {
                    "error": "Rate limit exceeded. Try again later.",
                    "limit": max_requests,
                    "window_seconds": window_seconds,
                }, 429

            # Add current timestamp to sorted set
            redis_client.zadd(key, {str(now): now})

            # Set expiration on the rate limit key
            redis_client.expire(key, window_seconds)

            return func(*args, **kwargs)

        wrapper.__name__ = func.__name__
        return wrapper

    return decorator
