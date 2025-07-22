from pathlib import Path
from os import getenv
from dotenv import load_dotenv

load_dotenv()
ENV = getenv("ENV")
BOT_TOKEN = getenv("BOT_TOKEN")
GPT_TOKEN = getenv("GPT_TOKEN")
API_VISION_TOKEN = getenv("API_VISION_TOKEN")
GPT_BASE_URL = getenv("GPT_BASE_URL")
REDIS_URL = getenv("REDIS_URL")
REDIS_DB = getenv("REDIS_DB")
MAX_HISTORY = getenv("MAX_HISTORY")

BASE_DIR = Path(__file__).parent.resolve()

