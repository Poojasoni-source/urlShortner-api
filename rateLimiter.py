import os
import redis
from fastapi import HTTPException, Request

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
except redis.ConnectionError:
    redis_client = None


def check_rate_limit(request: Request, limit: int = 10, window_seconds: int = 60):
    if redis_client is None:
        return  # Skip rate limiting if Redis is not running

    client_ip = request.client.host if request.client else "unknown"
    key = f"rate_limit:{client_ip}"

    current_count = redis_client.incr(key)
    if current_count == 1:
        redis_client.expire(key, window_seconds)

    if current_count > limit:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later.",
        )