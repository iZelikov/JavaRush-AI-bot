from itertools import cycle

from gpt.gpt_client import GPTClient
from utils import logger


class ClientsManager:
    def __init__(self):
        self._clients: list[GPTClient] = []
        self._iclients = cycle(self._clients)
        self._current_client = None

    def add_client(self, client: GPTClient):
        if isinstance(client, GPTClient) and client.client:
            self._clients.append(client)
            if len(self._clients) == 1:
                self.next_client()
        else:
            logger.warning(f'GPTClient не добавлен, неправильный формат: {client}')

    def get_client(self) -> GPTClient:
        return self._current_client

    def next_client(self):
        self._current_client = next(self._iclients)
        logger.info(f'♻️ Установлен клиент: {self._current_client.name}')
