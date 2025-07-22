import asyncio
import contextlib
from aiogram import Bot
from aiogram.enums import ChatAction
from aiogram.types import TelegramObject
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from typing import Any, Callable, Awaitable, Dict


class TypingMiddleware(BaseMiddleware):
    '''
    Должен автоматически добавлять "typing..." в моменты пока gpt обдумывает ответ.
    Как обычно, сгенерированный нейросетью кусок кода работает не, так как надо :(
    '''
    def __init__(self, interval: float = 3.0):
        self.interval = interval

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        bot: Bot = data["bot"]
        chat = data.get("event_chat")

        if not chat:
            return await handler(event, data)

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
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task