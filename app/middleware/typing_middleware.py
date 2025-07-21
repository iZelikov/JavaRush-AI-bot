from aiogram import BaseMiddleware
from aiogram.enums import ChatAction
from aiogram.types import TelegramObject
from typing import Callable, Awaitable, Dict, Any
import asyncio


class TypingMiddleware(BaseMiddleware):
    def __init__(self, interval: float = 3.0):
        self.interval = interval  # Интервал между "typing..." (сек)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        bot = data["bot"]
        chat = data.get("event_chat")

        if chat:
            stop_event = asyncio.Event()

            async def typing_loop():
                while not stop_event.is_set():
                    try:
                        await bot.send_chat_action(chat.id, ChatAction.TYPING)
                    except Exception:
                        break
                    await asyncio.sleep(self.interval)

            task = asyncio.create_task(typing_loop())

            try:
                return await handler(event, data)
            finally:
                stop_event.set()
                await task
        else:
            return await handler(event, data)