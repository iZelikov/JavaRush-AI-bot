import re

from aiogram.types import Message

from config import CHAT_GPT_TOKEN, CHAT_GPT_BASE_URL, CHAT_GPT_MODEL
from utils.gpt import GPT
from utils.help_load_res import load_prompt, get_cached_photo
from utils.help_messages import safe_markdown_edit


async def recognize_photo(file_url: str, message: Message, gpt: GPT):
    answer_message = await message.answer('Рассматривает фото...')
    img_response_text = await gpt.ask_image(
        file_url,
        prompt=load_prompt("image_recognition.txt"),
        token=CHAT_GPT_TOKEN,
        base_url=CHAT_GPT_BASE_URL,
        model=CHAT_GPT_MODEL
    )
    if img_response_text.startswith('ERROR'):
        await answer_message.edit_text(
            "Извини, братан! Фото конкретно не грузится. Может санкции, а может происки Масонов с Рептилоидами. Короче, давай другое.")
    else:
        await answer_message.edit_text('Думает, чего бы умного сказать...')
        response_text = await gpt.ask_once(
            message,
            prompt=load_prompt("blind.txt"),
            text=img_response_text,
            bot_message=answer_message)
        await safe_markdown_edit(answer_message, response_text)


def extract_image_urls(message: Message):
    IMAGE_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.tiff', '.heic'
    }
    IMAGE_URL_PATTERNS = {'image', 'img', 'media', 'avatar'}
    urls = extract_urls(message)
    image_urls = []
    for url in urls:
        lower_url = str(url).lower()
        if any(ext in lower_url for ext in IMAGE_EXTENSIONS):
            image_urls.append(url)
        elif any(pattern in lower_url for pattern in IMAGE_URL_PATTERNS):
            image_urls.append(url)
    return image_urls


async def send_photo(message: Message, img_name: str):
    try:
        photo = get_cached_photo(img_name)
        await message.answer_photo(photo=photo)
    except FileNotFoundError:
        await message.answer('ERROR: Братан, кажись тут была картинка, но я её потерял...')
    except Exception:
        await message.answer('ERROR: Крепись братан, происходит неведомая фигня!')


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
