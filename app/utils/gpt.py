from openai import OpenAI
from aiogram.types import Message

from config import GPT_TOKEN, GPT_BASE_URL
from utils.helpers import load_prompt
from utils.storage_factory import get_history_storage


class GPT:
    def __init__(self, gpt_key, base_url=None):
        self.client = OpenAI(api_key=gpt_key, base_url=base_url)
        self.storage = get_history_storage()
        self.prompt = load_prompt('base_prompt.txt')
        self.model = 'gpt-4o'
        self.max_tokens = 3000
        self.temperature = 0.8

    async def get_response(self, message: Message, prompt="") -> str:
        user_id = message.from_user.id
        request_text = message.text
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

        history.extend([
            {"role": "user", "content": request_text},
            {"role": "assistant", "content": answer_text}
        ])

        await self.storage.save_history(user_id, history)
        return answer_text


gpt = GPT(GPT_TOKEN, GPT_BASE_URL)
