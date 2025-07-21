from storage.abstract_storage import AbstractStorage
from collections import defaultdict
from typing import List, Dict, Optional, Any
import asyncio


class MemoryStorage(AbstractStorage):
    def __init__(self):
        self.history_storage = defaultdict(list)
        self.states = defaultdict(str)
        self.data = defaultdict(dict)
        self.lock = asyncio.Lock()

    async def get_history(self, user_id: int) -> List[Dict[str, str]]:
        async with self.lock:
            return self.history_storage[user_id].copy()

    async def save_history(self, user_id: int, history: List[Dict[str, str]]):
        async with self.lock:
            self.history_storage[user_id] = history

    async def reset_history(self, user_id: int):
        async with self.lock:
            if user_id in self.history_storage:
                del self.history_storage[user_id]

    async def get_state(self, user_id: int) -> Optional[str]:
        async with self.lock:
            return self.states.get(user_id)

    async def set_state(self, user_id: int, state: str):
        async with self.lock:
            self.states[user_id] = state

    async def get_data(self, user_id: int) -> Dict[str, Any]:
        async with self.lock:
            return self.data.get(user_id, {}).copy()

    async def update_data(self, user_id: int, data: Dict[str, Any]):
        async with self.lock:
            if user_id not in self.data:
                self.data[user_id] = {}
            self.data[user_id].update(data)

    async def reset_state(self, user_id: int):
        async with self.lock:
            if user_id in self.states:
                del self.states[user_id]
            if user_id in self.data:
                del self.data[user_id]