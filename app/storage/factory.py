import os
import sqlite3
from pathlib import Path

from storage.sqlite import SQLiteStorage
from storage.memory import MemoryStorage
from storage.redis import RedisStorage
from config import BASE_DIR


def get_storage():
    storage_type = os.getenv("STORAGE_TYPE", "memory")

    if storage_type == "sqlite":
        db_path = os.getenv("SQLITE_DB_PATH", Path(BASE_DIR.parent / 'data' / 'bot.db'))
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(db_path)
        return SQLiteStorage(conn)


    if storage_type == "redis":
        redis_url = os.getenv("REDIS_URL")
        ttl = int(os.getenv("REDIS_TTL", 3600))
        return RedisStorage(redis_url, ttl)

    # По умолчанию - in-memory хранилища
    return MemoryStorage()