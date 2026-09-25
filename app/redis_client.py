import os
from dotenv import load_dotenv
import redis

load_dotenv()

REDIS_URL = os.environ["REDIS_URL"]

redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True,
)


def is_rate_limited(
    key: str,
    limit: int = 10,
    window_seconds: int = 60,
) -> bool:
    """
    Returns True if the given key has exceeded `limit`
    requests within `window_seconds`.
    Uses a simple fixed-window counter.
    """
    current = redis_client.incr(key)

    if current == 1:
        redis_client.expire(key, window_seconds)

    return current > limit
