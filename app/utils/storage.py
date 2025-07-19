from abc import ABC, abstractmethod
from typing import List, Dict


class HistoryStorage(ABC):
    @abstractmethod
    async def get_history(self, user_id: int) -> List[Dict[str, str]]:
        pass

    @abstractmethod
    async def save_history(self, user_id: int, history: List[Dict[str, str]]):
        pass

    @abstractmethod
    async def reset_history(self, user_id: int):
        pass