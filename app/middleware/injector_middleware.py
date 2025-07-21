from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any
from aiogram.types import TelegramObject

from storage.abstract_storage import AbstractStorage
from utils.gpt import GPT
from storage.factory import get_storage

class InjectorMiddleware(BaseMiddleware):
    def __init__(self, gpt: GPT, storage: AbstractStorage):
        self.gpt = gpt
        self.storage = storage

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        data["gpt"] = self.gpt
        data["storage"] = self.storage
        return await handler(event, data)