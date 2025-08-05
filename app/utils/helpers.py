import hashlib
import re
from pathlib import Path

from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, FSInputFile, BufferedInputFile
from aiogram.utils.mypy_hacks import lru_cache

from config import BASE_DIR
from random import choice


@lru_cache(maxsize=256)
def load_text(filename: str | Path, fragment: int | None =0) -> str:
    text_filename = BASE_DIR / 'resources' / 'texts' / filename
    if fragment is None:
        return text_filename.read_text(encoding='utf-8')
    else:
        return text_filename.read_text(encoding='utf-8').split('\n\n')[fragment]


def rnd_text() -> str:
    texts = load_text('random_gopota.txt', fragment=None).split('\n\n')
    return choice(texts)


def load_sql(filename: str, fragment=0) -> str:
    sql_name = Path('sql', filename)
    return load_text(sql_name, fragment)


def load_prompt(filename: str) -> str:
    prompt_name = Path('prompts', filename)
    return load_text(prompt_name)


@lru_cache(maxsize=64)
def get_cached_photo(img_name: str) -> BufferedInputFile:
    img_path = BASE_DIR / 'resources' / 'images' / img_name
    if not img_path.exists():
        raise FileNotFoundError(f'Image {img_name} not found')
    img_bytes = img_path.read_bytes()
    file_hash = hashlib.md5(img_bytes).hexdigest()[:8]
    file_name = f"{img_path.stem}_{file_hash}{img_path.suffix}"
    return BufferedInputFile(img_bytes, filename=file_name)


async def send_photo(message: Message, img_name: str):
    try:
        photo = get_cached_photo(img_name)
        await message.answer_photo(photo=photo)
    except FileNotFoundError:
        await message.answer('ERROR: Братан, кажись тут была картинка, но я её потерял...')
    except Exception:
        await message.answer('ERROR: Крепись братан, происходит неведомая фигня!')


async def safe_markdown_send(message: Message, text: str, reply_markup=None):
    try:
        return await message.answer(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    except TelegramBadRequest:
        return await message.answer(text, parse_mode=None, reply_markup=reply_markup)


async def safe_markdown_edit(message: Message, text: str, reply_markup=None):
    try:
        return await message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    except TelegramBadRequest:
        return await message.edit_text(text, parse_mode=None, reply_markup=reply_markup)


def escape_markdown_v2(text: str) -> str:
    """
    Экранирует спецсимволы для Telegram MarkdownV2
    """
    escape_chars = r"_*[\]()~`>#+-=|{}.!\\"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


async def safe_markdown_v2_send(message: Message, text: str):
    try:
        escaped = escape_markdown_v2(text)
        return await message.answer(escaped, parse_mode=ParseMode.MARKDOWN_V2)
    except TelegramBadRequest:
        return await message.answer(text)


def extract_urls(message: Message) -> list:
    urls = []
    text = message.text or message.caption
    if message.entities:
        for entity in message.entities:
            if entity.type == "url":
                url = text[entity.offset: entity.offset + entity.length]
                urls.append(url)

            elif entity.type == "text_link":
                urls.append(entity.url)

    if not urls:
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)

    return urls


def extract_image_urls(message: Message):
    IMAGE_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.tiff', '.heic'
    }
    IMAGE_URL_PATTERNS = {'image', 'img', 'media'}
    urls = extract_urls(message)
    image_urls = []
    for url in urls:
        lower_url = str(url).lower()
        if any(ext in lower_url for ext in IMAGE_EXTENSIONS):
            image_urls.append(url)
        elif any(pattern in lower_url for pattern in IMAGE_URL_PATTERNS):
            image_urls.append(url)
    return image_urls
