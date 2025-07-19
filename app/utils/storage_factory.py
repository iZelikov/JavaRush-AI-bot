import os
from .storage_memory import MemoryStorage
from .storage_redis import RedisStorage
from config import ENV

def get_history_storage():
    env = ENV.lower()
    if env == "prod":
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            raise ValueError("REDIS_URL is required in production")
        return RedisStorage(redis_url)

    return MemoryStorage()