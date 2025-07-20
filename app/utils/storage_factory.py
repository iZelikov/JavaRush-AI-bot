import os
from .storage_memory import MemoryStorage
from .storage_redis import RedisStorage
from .storage_sqlite import SQLiteStorage
from config import ENV, REDIS_URL, BASE_DIR

def get_history_storage():
    env = ENV.lower()

    if env == "nas" or os.getenv("USE_SQLITE"):
        local_path = BASE_DIR.parent / 'data/chat_history.db'
        print(local_path)
        db_path = os.getenv("SQLITE_DB_PATH", local_path)
        return SQLiteStorage(db_path)

    if env == "prod":
        redis_url = REDIS_URL
        if not redis_url:
            raise ValueError("REDIS_URL is required in production")
        return RedisStorage(redis_url)

    return MemoryStorage()