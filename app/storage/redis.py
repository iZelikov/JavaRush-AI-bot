import json
from redis.asyncio import Redis
from storage.abstract_storage import AbstractStorage
from typing import List, Dict, Optional, Any


class RedisStorage(AbstractStorage):

    def __init__(self, redis_url: str, ttl: int = 3600):
        self.redis = Redis.from_url(redis_url)
        self.ttl = ttl

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

    async def get_state(self, user_id: int) -> Optional[str]:
        return await self.redis.get(f"user:{user_id}:state")

    async def set_state(self, user_id: int, state: str):
        await self.redis.setex(f"user:{user_id}:state", self.ttl, state)

    async def get_data(self, user_id: int) -> Dict[str, Any]:
        data = await self.redis.get(f"user:{user_id}:data")
        return json.loads(data) if data else {}

    async def update_data(self, user_id: int, data: Dict[str, Any]):
        current_data = await self.get_data(user_id)
        current_data.update(data)
        await self.redis.setex(
            f"user:{user_id}:data",
            self.ttl,
            json.dumps(current_data)
        )

    async def reset_state(self, user_id: int):
        await self.redis.delete(f"user:{user_id}:state")
        await self.redis.delete(f"user:{user_id}:data")
