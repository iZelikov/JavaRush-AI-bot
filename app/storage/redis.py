import json

from aiogram.fsm.storage.base import StorageKey, StateType
from redis.asyncio import Redis
from storage.abstract_storage import AbstractStorage
from typing import List, Dict, Optional, Any


class RedisStorage(AbstractStorage):

    def __init__(self, redis_url: str, ttl: int = 3600):
        self.redis = Redis.from_url(
            redis_url, encoding="utf-8", decode_responses=True
        )
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

    async def get_state(self, key: StorageKey) -> Optional[str]:
        return await self.redis.get(f"user:{key.user_id}:state")

    async def set_state(self, key: StorageKey, state: Optional[StateType]) -> None:
        key_name = f"user:{key.user_id}:state"
        if state is None:
            # удаляем состояние, вместо записи None
            await self.redis.delete(key_name)
        else:
            # state.state — строковое имя State
            await self.redis.setex(key_name, self.ttl, state.state)

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        data = await self.redis.get(f"user:{key.user_id}:data")
        return json.loads(data) if data else {}

    async def set_data(self, key: StorageKey, data: Dict[str, Any]):
        await self.redis.setex(
            f"user:{key.user_id}:data",
            self.ttl,
            json.dumps(data)
        )

    async def update_data(self, key: StorageKey, data: Dict[str, Any]):
        current_data = await self.get_data(key)
        current_data.update(data)
        await self.redis.setex(
            f"user:{key.user_id}:data",
            self.ttl,
            json.dumps(current_data)
        )

    async def reset_state(self, key: StorageKey):
        await self.redis.delete(f"user:{key.user_id}:state")
        await self.redis.delete(f"user:{key.user_id}:data")

    async def close(self) -> None:
        await self.redis.close()
