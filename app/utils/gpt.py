import asyncio
import os
import logging
from typing import Optional, List, Dict, Union

from aiogram.enums import ChatAction
from aiogram.types import Message
from openai import OpenAI, RateLimitError, APIError, APITimeoutError, Stream, AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletionChunk

from storage.abstract_storage import AbstractStorage
from utils.help_load_res import load_prompt

logger = logging.getLogger(__name__)


class GPT:
    def __init__(self, gpt_key: str, db: AbstractStorage, base_url: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=gpt_key, base_url=base_url)
        self.token = gpt_key
        self.base_url = base_url
        self.storage = db
        self.prompt = load_prompt('base_prompt.txt')
        self.model = os.getenv('GPT_MODEL') or 'deepseek-r1-0528:free'
        self.max_tokens = 3000
        self.temperature = 0.8

    def _clear_think(self, text: str) -> str:
        return text.split('</think>')[-1].strip()

    async def _send_chat_completion(
            self,
            messages: List[Dict],
            model: Optional[str] = None,
            max_tokens: Optional[int] = None,
            temperature: Optional[float] = None,
            client: Optional[AsyncOpenAI] = None,
            stream: bool = False
    ) -> Union[str, AsyncStream[ChatCompletionChunk]]:
        model = model or self.model
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature if temperature is not None else self.temperature
        client = client if client is not None else self.client

        try:
            if not stream:
                # Асинхронный вызов для обычного ответа
                response = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                answer_text = response.choices[0].message.content.strip()
                return self._clear_think(answer_text)
            else:
                # Возвращаем асинхронный генератор для потоковой передачи
                return await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=True
                )

        except RateLimitError:
            logger.warning("Rate limit exceeded")
            return 'ERROR: Братан, GPT токен слегка протух, то бишь исчерпал лимит. Обожди чутка... Максимум до завтра.'

        except APITimeoutError:
            logger.error("GPT API timeout")
            return 'ERROR: GPT молчит как рыба об лёд. Попробуй позже.'

        except APIError as e:
            logger.error(f"OpenAI API Error: {e}")
            return 'ERROR: Электронный болван говорит, что у тебя GPT API не такой как у него.'

        except Exception as e:
            logger.exception(f"Неизвестная ошибка при запросе к GPT: {e}")
            return 'ERROR: Произошла неведомая фигня... GPT ушёл в отказ.'

    async def _handle_stream(self, stream: AsyncStream[ChatCompletionChunk], message: Message) -> str:
        temp_msg = await message.answer('...')
        buffer = []
        last_update = asyncio.get_event_loop().time()
        update_interval = 0.5

        async for chunk in stream:
            part = chunk.choices[0].delta.content
            if part:
                buffer.append(part)
            current_time = asyncio.get_event_loop().time()
            if current_time - last_update >= update_interval and buffer:
                temp_msg = await self._send_part(temp_msg, buffer)
                last_update = current_time
                buffer = []

        if buffer:
            temp_msg = await self._send_part(temp_msg, buffer)

        full_text = temp_msg.text.lstrip('.')
        await temp_msg.delete()
        return full_text

    async def _send_part(self, message: Message, buffer: list[str]) -> Message:
        new_part = ''.join(buffer)
        if not new_part:
            return message

        new_text = f'{message.text}{new_part}'

        try:
            return await message.edit_text(new_text, parse_mode=None)
        except Exception as e:
            print(f"Ошибка при редактировании сообщения: {e}")
            return message

    async def _get_text_from_stream(self,
                                    messages: list[dict],
                                    message: Message):
        response_stream = await self._send_chat_completion(messages=messages, stream=True)

        if isinstance(response_stream, str):
            return response_stream

        response_text = await self._handle_stream(response_stream, message)
        return response_text

    async def dialog(self, message: Message, prompt: str = "", text="") -> str:
        user_id = message.from_user.id
        request_text = text or message.text or message.caption or ""

        history = await self.storage.get_history(user_id)

        messages = [
            {"role": "system", "content": f"{self.prompt}\n{prompt}"},
            *history,
            {"role": "user", "content": request_text}
        ]

        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

        response_text = await self._get_text_from_stream(messages, message)

        history += [
            {"role": "user", "content": request_text},
            {"role": "assistant", "content": response_text}
        ]
        await self.storage.save_history(user_id, history)
        return response_text

    async def ask_once(self, message: Message, prompt: str = "", text="") -> str:
        request_text = text or message.text or message.caption or ""

        messages = [
            {"role": "system", "content": self.prompt + prompt},
            {"role": "user", "content": request_text}
        ]
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

        response_text = await self._get_text_from_stream(messages, message)

        return response_text

    async def ask_image(
            self,
            img_url,
            prompt: str = "Опиши всё что видишь на картинке",
            token: str = None,
            base_url: str = None, model=None) -> str:
        token = token or self.token
        base_url = base_url or self.base_url
        model = model or "gpt-4-turbo"
        client = AsyncOpenAI(api_key=token, base_url=base_url)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"{prompt}"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"{img_url}"
                        }
                    }
                ]
            }
        ]
        response = await self._send_chat_completion(
            messages=messages,
            model=model,
            client=client,
            stream=False
        )
        return response

