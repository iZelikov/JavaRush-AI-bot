import base64
import os

import aiohttp
import logging
from typing import Optional, List, Dict

from aiogram.enums import ChatAction
from aiogram.types import Message
from openai import OpenAI, RateLimitError, APIError, Timeout
from storage.abstract_storage import AbstractStorage
from utils.helpers import load_prompt
from config import CHAT_GPT_TOKEN, CHAT_GPT_BASE_URL, CHAT_GPT_MODEL

logger = logging.getLogger(__name__)


class GPT:
    def __init__(self, gpt_key: str, db: AbstractStorage, base_url: Optional[str] = None):
        self.client = OpenAI(api_key=gpt_key, base_url=base_url)
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
            client=None
    ) -> str:
        model = model or self.model
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature if temperature is not None else self.temperature
        client = client if client is not None else self.client

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            answer_text = response.choices[0].message.content.strip()
            return self._clear_think(answer_text)


        except RateLimitError:
            logger.warning("Rate limit exceeded")
            return 'Братан, GPT токен слегка протух, то бишь исчерпал лимит. Обожди чутка... Максимум до завтра.'

        except Timeout:
            logger.error("GPT API timeout")
            return 'GPT молчит как рыба об лёд. Попробуй позже.'

        except APIError as e:
            logger.error(f"OpenAI API Error: {e}")
            return 'Электронный болван говорит, что у тебя GPT API не такой как у него.'

        except Exception as e:
            logger.exception(f"Неизвестная ошибка при запросе к GPT: {e}")
            return 'Произошла неведомая фигня... GPT ушёл в отказ.'

    async def dialog(self, message: Message, prompt: str = "", text="") -> str:
        user_id = message.from_user.id
        request_text = text or message.text or message.caption or ""

        history = await self.storage.get_history(user_id)

        messages = [
            {"role": "system", "content": self.prompt + prompt},
            *history,
            {"role": "user", "content": request_text}
        ]

        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        response_text = await self._send_chat_completion(messages=messages)

        # Обновление истории
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
        return await self._send_chat_completion(messages=messages)

    async def ask_image(self, img_url, prompt: str = "Опиши всё что видишь на картинке"):

        client = OpenAI(api_key=CHAT_GPT_TOKEN, base_url=CHAT_GPT_BASE_URL)
        model = CHAT_GPT_MODEL or "gpt-4-turbo"
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
        return await  self._send_chat_completion(messages=messages, model=model, client=client)
