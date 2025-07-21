from abc import abstractmethod
from typing import List, Dict, Any, Optional

from aiogram.fsm.storage.base import BaseStorage, StorageKey


class AbstractStorage(BaseStorage):
    @abstractmethod
    async def get_history(self, user_id: int) -> List[Dict[str, str]]:
        pass

    @abstractmethod
    async def save_history(self, user_id: int, history: List[Dict[str, str]]):
        pass

    @abstractmethod
    async def reset_history(self, user_id: int):
        pass

    @abstractmethod
    async def get_state(self, key: StorageKey) -> Optional[str]:
        pass

    @abstractmethod
    async def set_state(self, key: StorageKey, state: str):
        pass

    @abstractmethod
    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def set_data(self, key: StorageKey, data: Dict[str, Any]):
        pass

    @abstractmethod
    async def update_data(self, key: StorageKey, data: Dict[str, Any]):
        pass

    @abstractmethod
    async def reset_state(self, key: StorageKey):
        pass

    @abstractmethod
    async def close(self):
        pass
