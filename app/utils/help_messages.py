import re

from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

MAX_TEXT_LENGTH = 4000


async def safe_markdown_answer(message: Message, text: str, reply_markup=None):
    if len(text) > MAX_TEXT_LENGTH:
        break_index = text[:MAX_TEXT_LENGTH].rfind('\n')
        if break_index <= 0:
            break_index = MAX_TEXT_LENGTH
        await safe_markdown_answer(message, text[:break_index])
        await safe_markdown_answer(message, text[break_index:], reply_markup=reply_markup)
        return None
    collapsed_text = collapse_md(text)
    escaped_text = escape_md(collapsed_text)
    try:
        return await message.answer(
            escaped_text,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=reply_markup)
    except TelegramBadRequest:
        try:
            clear_text = remove_md2(collapsed_text)
            return await message.answer(
                clear_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup)
        except TelegramBadRequest:
            clear_text = remove_md_all(text)
            return await message.answer(
                clear_text,
                parse_mode=None,
                reply_markup=reply_markup)


async def safe_markdown_edit(message: Message, text: str, reply_markup=None):
    if len(text) > MAX_TEXT_LENGTH:
        break_index = text[:MAX_TEXT_LENGTH].rfind('\n')
        if break_index <= 0:
            break_index = MAX_TEXT_LENGTH
        await safe_markdown_edit(message, text[:break_index])
        await safe_markdown_answer(message, text[break_index:], reply_markup=reply_markup)
        return None
    collapsed_text = collapse_md(text)
    escaped_text = escape_md(collapsed_text)
    try:
        return await message.edit_text(
            escaped_text,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=reply_markup)
    except TelegramBadRequest:
        try:
            clear_text = remove_md2(collapsed_text)
            return await message.edit_text(
                clear_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup)
        except TelegramBadRequest:
            clear_text = remove_md_all(text)
            return await message.edit_text(
                clear_text,
                parse_mode=None,
                reply_markup=reply_markup)


def escape_md(text: str) -> str:
    escaped1 = r'([\[\]()>#+\-={}.!\\])'
    replace1 = r'\\\1'
    escaped2 = r'([a-zA-Zа-яА-ЯёЁ0-9]+)([_*~`|])([a-zA-Zа-яА-ЯёЁ0-9]+)'
    replace2 = r'\1\\\2\3'
    if not text:
        return text
    e_text = re.sub(escaped1, replace1, text)
    e_text = re.sub(escaped2, replace2, e_text)
    return e_text


def remove_md_all(text: str) -> str:
    return re.sub(r'[_*~`|]', '', text)

def remove_md2(text: str) -> str:
    return re.sub(r'[~|]', '', text)


def collapse_md(text: str) -> str:
    c_text = re.sub(r'([~*]){2,}', r'\1', text)
    c_text = re.sub(r'([|_]){3,}', r'\1\1', c_text)
    return c_text
