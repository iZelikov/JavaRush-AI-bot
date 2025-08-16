import re

from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from utils.help_load_res import get_cached_photo


async def safe_markdown_answer(message: Message, text: str, reply_markup=None):
    try:
        escaped_text = escape_md(text)
        return await message.answer(
            escaped_text,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=reply_markup)
    except TelegramBadRequest:
        try:
            return await message.answer(
                text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup)
        except TelegramBadRequest:
            return await message.answer(
                text,
                parse_mode=None,
                reply_markup=reply_markup)


async def safe_markdown_edit(message: Message, text: str, reply_markup=None):
    if len(text) > 4000:
        print("Сообщение слишком длинное")
        return message
    try:
        escaped_text = escape_md(text)
        return await message.edit_text(
            escaped_text,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=reply_markup)
    except TelegramBadRequest:
        try:
            return await message.edit_text(
                text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup)
        except TelegramBadRequest:
            return await message.edit_text(
                text,
                parse_mode=None,
                reply_markup=reply_markup)


def escape_md(text: str) -> str:
    """
    Экранирует спецсимволы для Telegram MarkdownV2 кроме используемых в разметке
    """
    _MDV2_RE = re.compile(r'([\[\]()>#+\-={}.!\\])')
    if not text:
        return text
    return _MDV2_RE.sub(r'\\\1', text)


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


async def send_photo(message: Message, img_name: str):
    try:
        photo = get_cached_photo(img_name)
        await message.answer_photo(photo=photo)
    except FileNotFoundError:
        await message.answer('ERROR: Братан, кажись тут была картинка, но я её потерял...')
    except Exception:
        await message.answer('ERROR: Крепись братан, происходит неведомая фигня!')


