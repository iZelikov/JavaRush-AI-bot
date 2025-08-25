from config import GPT_TOKEN, GPT_BASE_URL, GPT_MODEL, CHAT_GPT_TOKEN, CHAT_GPT_MODEL, CHAT_GPT_BASE_URL
from gpt.clients_manager import ClientsManager
from gpt.gpt_client import GPTClient

client1 = GPTClient(GPT_TOKEN, GPT_MODEL, GPT_BASE_URL)
client2 = GPTClient(CHAT_GPT_TOKEN, CHAT_GPT_MODEL, CHAT_GPT_BASE_URL)

manager = ClientsManager()
manager.add_client(client1)
manager.add_client(client2)

print(manager.get_client())
manager.next_client()
print(manager.get_client())
manager.next_client()
print(manager.get_client())
manager.next_client()
print(manager.get_client())
print(manager.get_client().model)
