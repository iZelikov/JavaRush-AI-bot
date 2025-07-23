from aiogram.types import Message
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from typing import Any, Callable, Awaitable, Dict

from aiogram.utils.chat_action import ChatActionSender


class TypingMiddleware(BaseMiddleware):
    '''
    Должен автоматически добавлять "typing..." в моменты пока gpt обдумывает ответ.
    Как обычно, сгенерированный нейросетью кусок кода работает не, так как надо :(
    Приходится по старинке добавлять вызов вручную в тех местах где требуется.
    '''

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        async with ChatActionSender(
                action='typing',
                chat_id= data.get("event_chat").id,
                bot=data["bot"],
        ):
            return await handler(event, data)
