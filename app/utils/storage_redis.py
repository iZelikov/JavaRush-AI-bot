import json
import os
from redis.asyncio import Redis
from .storage import HistoryStorage
from typing import List, Dict


class RedisStorage(HistoryStorage):
    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(redis_url)
        self.ttl = 3600  # 1 час

    async def get_history(self, user_id: int) -> List[Dict[str, str]]:
        key = f"user:{user_id}:messages"
        history = await self.redis.get(key)
        return json.loads(history) if history else []

    async def save_history(self, user_id: int, history: List[Dict[str, str]]):
        key = f"user:{user_id}:messages"
        await self.redis.setex(key, self.ttl, json.dumps(history))

    async def reset_history(self, user_id: int):
        key = f"user:{user_id}:messages"
        await self.redis.delete(key)