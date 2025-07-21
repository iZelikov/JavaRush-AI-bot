import base64

import aiohttp
from openai import OpenAI
from aiogram.types import Message

from storage.abstract_storage import AbstractStorage
from utils.helpers import load_prompt
from config import GPT_TOKEN


class GPT:
    def __init__(self, gpt_key, db: AbstractStorage, base_url=None):
        self.client = OpenAI(api_key=gpt_key, base_url=base_url)
        self.storage = db
        self.prompt = load_prompt('base_prompt.txt')
        self.model = 'gpt-4o'
        self.max_tokens = 3000
        self.temperature = 0.8

    async def get_response(self, message: Message, prompt="") -> str:
        user_id = message.from_user.id
        request_text = message.text or message.caption or ""
        history = await self.storage.get_history(user_id)

        messages = [
                       {"role": "system", "content": self.prompt + prompt}
                   ] + history + [{"role": "user", "content": request_text}]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

        answer_text = response.choices[0].message.content

        history += [
            {"role": "user", "content": request_text},
            {"role": "assistant", "content": answer_text}
        ]

        await self.storage.save_history(user_id, history)
        return answer_text

    async def ask_once(self, message: Message, prompt=''):
        user_id = message.from_user.id
        request_text = message.text or message.caption or ""

        messages = [
            {"role": "system", "content": self.prompt + prompt},
            {"role": "user", "content": request_text}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

        answer_text = response.choices[0].message.content
        return answer_text

    async def ask_gpt_vision(self, image_bytes: bytes, prompt: str = "Что изображено на этом фото?") -> str:
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        headers = {
            "Authorization": f"Bearer {GPT_TOKEN}",
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

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload) as resp:
                data = await resp.json()

                print("GPT VISION RESPONSE:", data)

                if "choices" not in data:
                    raise ValueError(f"OpenAI ответ не содержит 'choices': {data}")

                return data["choices"][0]["message"]["content"]