from .storage import HistoryStorage
from collections import defaultdict
from typing import List, Dict
import asyncio


class MemoryStorage(HistoryStorage):
    def __init__(self):
        self.storage = defaultdict(list)
        self.lock = asyncio.Lock()

    async def get_history(self, user_id: int) -> List[Dict[str, str]]:
        async with self.lock:
            return self.storage[user_id].copy()

    async def save_history(self, user_id: int, history: List[Dict[str, str]]):
        async with self.lock:
            self.storage[user_id] = history

    async def reset_history(self, user_id: int):
        async with self.lock:
            if user_id in self.storage:
                del self.storage[user_id]
