import re

from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message


async def safe_markdown_answer(message: Message, text: str, reply_markup=None):
    if len(text) > 4000:
        await safe_markdown_answer(message, text[:4000])
        await safe_markdown_answer(message, text[4000:], reply_markup=reply_markup)
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
        await safe_markdown_edit(message, text[:4000])
        await safe_markdown_answer(message, text[4000:], reply_markup=reply_markup)
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
