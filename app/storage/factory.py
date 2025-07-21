import os
import sqlite3
from pathlib import Path

from storage.sqlite import SQLiteHistoryStorage, SQLiteStateStorage
from storage.memory import MemoryStateStorage, MemoryHistoryStorage
from storage.redis import RedisStateStorage, RedisHistoryStorage
from config import BASE_DIR


def create_storages():
    storage_type = os.getenv("STORAGE_TYPE", "memory")

    if storage_type == "sqlite":
        db_path = os.getenv("SQLITE_DB_PATH", Path(BASE_DIR.parent / 'data' / 'bot.db'))
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(db_path)
        return (
            SQLiteStateStorage(conn),
            SQLiteHistoryStorage(conn)
        )

    if storage_type == "redis":
        redis_url = os.getenv("REDIS_URL")
        ttl = int(os.getenv("REDIS_TTL", 3600))
        return (
            RedisStateStorage(redis_url, ttl),
            RedisHistoryStorage(redis_url, ttl)
        )

    # По умолчанию - in-memory хранилища
    return MemoryStateStorage(), MemoryHistoryStorage()

create_storages()