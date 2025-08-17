import re

from aiogram.types import Message

from utils.gpt import GPT
from utils.help_load_res import load_prompt, get_cached_photo
from utils.help_messages import safe_markdown_edit


async def recognize_photo(file_url: str, message: Message, gpt: GPT):
    answer_message = await message.answer('Рассматривает фото...')
    img_response_text = await gpt.ask_image(
        file_url,
        prompt=load_prompt("image_recognition.txt"),
    )
    if img_response_text.startswith('ERROR'):
        await answer_message.edit_text(
            "Извини, братан! Фото конкретно не грузится. Может санкции, а может происки Масонов с Рептилоидами. Или администратор GPT-модель неправильную прикрутил, которая фото не распознаёт (надо gpt-4 и выше).")
    else:
        await answer_message.edit_text('Думает, чего бы умного сказать...')
        response_text = await gpt.ask_once(
            message,
            prompt=load_prompt("blind.txt"),
            text=img_response_text,
            output_message=answer_message)
        await safe_markdown_edit(answer_message, response_text)


def extract_image_urls(message: Message):
    image_extensions = {
        '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.tiff', '.heic'
    }
    image_url_patterns = {'image', 'img', 'media', 'avatar'}
    urls = extract_urls(message)
    image_urls = []
    for url in urls:
        lower_url = str(url).lower()
        if any(ext in lower_url for ext in image_extensions):
            image_urls.append(url)
        elif any(pattern in lower_url for pattern in image_url_patterns):
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
