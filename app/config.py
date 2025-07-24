from pathlib import Path
from os import getenv
from dotenv import load_dotenv

load_dotenv()
ENV = getenv("ENV")
BOT_TOKEN = getenv("BOT_TOKEN")
GPT_TOKEN = getenv("GPT_TOKEN")
GPT_BASE_URL = getenv("GPT_BASE_URL")
GPT_MODEL = getenv("GPT_MODEL")
CHAT_GPT_TOKEN = getenv("CHAT_GPT_TOKEN")
CHAT_GPT_BASE_URL = getenv("CHAT_GPT_BASE_URL")
CHAT_GPT_MODEL = getenv("CHAT_GPT_MODEL")
REDIS_URL = getenv("REDIS_URL")
REDIS_DB = getenv("REDIS_DB")
MAX_HISTORY = getenv("MAX_HISTORY")

BASE_DIR = Path(__file__).parent.resolve()

