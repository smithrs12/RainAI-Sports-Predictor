# common/redis_cache.py
import os, redis
from common.logger import logger

_redis = None

def get_redis():
    global _redis
    if _redis:
        return _redis
    url = os.getenv("REDIS_URL")
    if not url:
        logger.warning("No REDIS_URL provided; running without cache.")
        return None
    _redis = redis.Redis.from_url(url, decode_responses=True, ssl=True)
    _redis.ping()
    logger.info("✅ Redis connected")
    return _redis
