from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class AbstractStorage(ABC):
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
    async def get_state(self, user_id: int) -> Optional[str]:
        pass

    @abstractmethod
    async def set_state(self, user_id: int, state: str):
        pass

    @abstractmethod
    async def get_data(self, user_id: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def update_data(self, user_id: int, data: Dict[str, Any]):
        pass

    @abstractmethod
    async def reset_state(self, user_id: int):
        pass