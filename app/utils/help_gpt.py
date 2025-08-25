from config import GPT_TOKEN, GPT_BASE_URL, GPT_MODEL, CHAT_GPT_TOKEN, CHAT_GPT_MODEL, CHAT_GPT_BASE_URL
from gpt.clients_manager import ClientsManager
from gpt.gpt_client import GPTClient

tokens = GPT_TOKEN.split(',')
chat_gpt_tokens = CHAT_GPT_TOKEN.split(',')

manager = ClientsManager()
for token in tokens:
    manager.add_client(GPTClient(token, GPT_MODEL, GPT_BASE_URL))

chat_gpt_manager = ClientsManager()
for token in chat_gpt_tokens:
    chat_gpt_manager.add_client(GPTClient(token, CHAT_GPT_MODEL, CHAT_GPT_BASE_URL))
