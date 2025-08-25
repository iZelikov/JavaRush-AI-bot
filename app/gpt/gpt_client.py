from openai import AsyncOpenAI

from utils import logger


class GPTClient:
    def __init__(self, token: str, model: str, base_url: str = None):

        try:
            self.client = AsyncOpenAI(
                api_key=token,
                base_url=base_url)
            self.model = model
            self.name = f'{model}:{token[-6:]}'
            logger.info(f'создан GPTClient {self.name}')
        except Exception as e:
            self.client = None
            logger.exception(f'Не удалось создать GPTClient: {e}')

    def __str__(self):
        return f"GPTClient: {self.name}"

    def __repr__(self):
        return str(self)


