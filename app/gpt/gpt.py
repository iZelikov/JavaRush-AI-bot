import asyncio
from typing import Optional, List, Dict, Union

from aiogram.enums import ChatAction
from aiogram.types import Message, CallbackQuery
from openai import AsyncOpenAI, AsyncStream, RateLimitError, APITimeoutError, APIError
from openai.types.chat import ChatCompletionChunk

from storage.abstract_storage import AbstractStorage
from utils import logger


class GPT:

    def __init__(
            self,
            gpt_key: str,
            model: str,
            db: AbstractStorage,
            base_prompt: str = "",
            base_url: Optional[str] = None,
            chat_gpt_key: Optional[str] = None,
            chat_gpt_base_url: Optional[str] = None,
            chat_gpt_model: Optional[str] = None,
    ):
        self.client = AsyncOpenAI(
            api_key=gpt_key,
            base_url=base_url)
        self.storage = db
        self.base_prompt = base_prompt
        self.model = model
        self.max_tokens = 3000
        self.temperature = 0.8
        self.chat_gpt_model = chat_gpt_model or model
        self.chat_gpt_client = self.client
        if chat_gpt_key:
            self.chat_gpt_client = AsyncOpenAI(
                api_key=chat_gpt_key,
                base_url=chat_gpt_base_url)

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
            logger.warning("😤 Нету токенов - нету мультиков!")
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

    async def _handle_stream(
            self,
            stream: AsyncStream[ChatCompletionChunk],
            output_message: Message = None) -> str:

        full_text_parts = []
        buffer = []

        if output_message:
            current_message = await output_message.edit_text('...')
            last_update = asyncio.get_event_loop().time()
            update_interval = 1

            async for chunk in stream:
                part = chunk.choices[0].delta.content
                if part is None:
                    continue

                buffer.append(part)
                full_text_parts.append(part)

                current_time = asyncio.get_event_loop().time()
                if current_time - last_update >= update_interval and buffer:
                    current_message = await self._send_part(current_message, buffer)
                    buffer = []
                    last_update = current_time

            if buffer:
                current_message = await self._send_part(current_message, buffer)

            full_text = ''.join(full_text_parts)
        else:
            async for chunk in stream:
                part = chunk.choices[0].delta.content
                if part:
                    full_text_parts.append(part)
            full_text = ''.join(full_text_parts)
        return full_text

    async def _send_part(self, message: Message, buffer: list[str]) -> Message:
        if not buffer:
            return message
        max_length = 3500
        old_text = message.text
        new_part = ''.join(buffer)
        if new_part == '':
            return message

        if len(old_text) > max_length:
            loading_str = '\n\n=+=+= LOADING =+=+=\n'
            if not loading_str in old_text:
                old_text+=loading_str
            new_part = '#'

        try:
            new_text = f'{old_text}{new_part}'
            return await message.edit_text(new_text, parse_mode=None)

        except Exception as e:
            logger.error(f"Ошибка при редактировании сообщения: {e}")
            return message

    async def _get_text_from_stream(self,
                                    messages: list[dict],
                                    output_message: Message = None):
        response_stream = await self._send_chat_completion(messages=messages, stream=True)

        if isinstance(response_stream, str):
            return response_stream

        response_text = await self._handle_stream(response_stream, output_message)
        return response_text

    async def dialog(self,
                     user_message: Message | CallbackQuery,
                     prompt: str = "",
                     text: str = "",
                     output_message: Message = None) -> str:

        user_id = user_message.from_user.id
        if isinstance(user_message, CallbackQuery):
            user_message = user_message.message
        request_text = text or user_message.text or user_message.caption or ""

        history = await self.storage.get_history(user_id)

        messages = [
            {"role": "system", "content": f"{self.base_prompt}\n{prompt}"},
            *history,
            {"role": "user", "content": request_text}
        ]

        await user_message.bot.send_chat_action(chat_id=user_message.chat.id, action=ChatAction.TYPING)

        response_text = await self._get_text_from_stream(messages, output_message)

        history += [
            {"role": "user", "content": request_text},
            {"role": "assistant", "content": response_text}
        ]
        await self.storage.save_history(user_id, history)
        return response_text

    async def ask_once(self,
                       user_message: Message | CallbackQuery,
                       prompt: str = "",
                       text: str = "",
                       output_message: Message = None) -> str:
        if isinstance(user_message, CallbackQuery):
            user_message = user_message.message
        request_text = text or user_message.text or user_message.caption or ""

        messages = [
            {"role": "system", "content": self.base_prompt + prompt},
            {"role": "user", "content": request_text}
        ]
        await user_message.bot.send_chat_action(chat_id=user_message.chat.id, action=ChatAction.TYPING)

        response_text = await self._get_text_from_stream(messages, output_message)

        return response_text

    async def ask_image(
            self,
            img_url,
            prompt: str = "Опиши всё что видишь на картинке",
    ) -> str:
        model = self.chat_gpt_model
        client = self.chat_gpt_client
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
