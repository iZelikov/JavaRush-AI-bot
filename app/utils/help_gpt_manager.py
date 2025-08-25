from config import GPT_TOKEN, GPT_BASE_URL, GPT_MODEL, CHAT_GPT_TOKEN, CHAT_GPT_MODEL, CHAT_GPT_BASE_URL, RESERVE_TOKEN, \
    RESERVE_MODEL, RESERVE_URL
from gpt.clients_manager import ClientsManager
from gpt.gpt_client import GPTClient


def add_clients(
        clients_manager: ClientsManager,
        tokens_string: str,
        model: str,
        base_url: str = None):
    tokens = tokens_string.split(',')
    for token in tokens:
        clients_manager.add_client(GPTClient(token, model, base_url))


manager = ClientsManager()
add_clients(manager, GPT_TOKEN, GPT_MODEL, GPT_BASE_URL)

if RESERVE_TOKEN:
    add_clients(manager, RESERVE_TOKEN, RESERVE_MODEL, RESERVE_URL)

chat_gpt_manager = None
if CHAT_GPT_TOKEN:
    chat_gpt_manager = ClientsManager()
    add_clients(chat_gpt_manager, CHAT_GPT_TOKEN, CHAT_GPT_MODEL, CHAT_GPT_BASE_URL)
