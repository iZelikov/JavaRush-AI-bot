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
from config import API_VISION_TOKEN

logger = logging.getLogger(__name__)


class GPT:
    def __init__(self, gpt_key: str, db: AbstractStorage, base_url: Optional[str] = None):
        self.client = OpenAI(api_key=gpt_key, base_url=base_url)
        self.storage = db
        self.prompt = load_prompt('base_prompt.txt')
        self.model = os.getenv('GPT_MODEL') or 'gpt-4o'
        self.max_tokens = 3000
        self.temperature = 0.8

    async def _send_chat_completion(
            self,
            messages: List[Dict],
            model: Optional[str] = None,
            max_tokens: Optional[int] = None,
            temperature: Optional[float] = None,
    ) -> str:
        model = model or self.model
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature if temperature is not None else self.temperature

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()

        except RateLimitError:
            logger.warning("Rate limit exceeded")
            return 'Братан, GPT токен слегка протух, то бишь исчерпал лимит. Обожди чутка.'

        except Timeout:
            logger.error("GPT API timeout")
            return 'GPT молчит как рыба об лёд. Попробуй позже.'

        except APIError as e:
            logger.error(f"OpenAI API Error: {e}")
            return 'Электронный болван говорит, что у тебя GPT API не такой как у него.'

        except Exception as e:
            logger.exception(f"Неизвестная ошибка при запросе к GPT: {e}")
            return 'Произошла неведомая фигня... GPT ушёл в отказ.'

    async def dialog(self, message: Message, prompt: str = "") -> str:
        user_id = message.from_user.id
        request_text = message.text or message.caption or ""

        history = await self.storage.get_history(user_id)

        messages = [
            {"role": "system", "content": self.prompt + prompt},
            *history,
            {"role": "user", "content": request_text}
        ]

        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        response_text = await self._send_chat_completion(messages)

        # Обновление истории
        history += [
            {"role": "user", "content": request_text},
            {"role": "assistant", "content": response_text}
        ]
        await self.storage.save_history(user_id, history)
        return response_text

    async def ask_once(self, message: Message, prompt: str = "") -> str:
        request_text = message.text or message.caption or ""

        messages = [
            {"role": "system", "content": self.prompt + prompt},
            {"role": "user", "content": request_text}
        ]
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        return await self._send_chat_completion(messages)

    async def ask_gpt_vision(self, image_bytes: bytes, prompt: str = "Что изображено на этом фото?") -> str:
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        headers = {
            "Authorization": f"Bearer {API_VISION_TOKEN}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                    ],
                }
            ],
            "max_tokens": 1000
        }

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
                async with session.post("https://api.openai.com/v1/chat/completions", headers=headers,
                                        json=payload) as resp:
                    data = await resp.json()
                    logger.debug("GPT VISION RESPONSE: %s", data)

                    if "choices" not in data:
                        raise ValueError(f"OpenAI ответ не содержит 'choices': {data}")

                    return data["choices"][0]["message"]["content"].strip()

        except aiohttp.ClientError as e:
            logger.exception("Ошибка при запросе GPT Vision")
            return "GPT Vision зазнался и не отвечает. Может у тя инет барахлит или токен не такой?."

        except Exception as e:
            logger.exception("Непредвиденная ошибка GPT Vision")
            return "Картинка битая пришла или ещё какая фигня приключилась. Скинь другую!"
