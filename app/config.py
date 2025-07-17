from pathlib import Path
from os import getenv
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = getenv("BOT_TOKEN")
GPT_TOKEN = getenv("GPT_TOKEN")
GPT_BASE_URL = getenv("GPT_BASE_URL")

BASE_DIR = Path(__file__).parent.resolve()
