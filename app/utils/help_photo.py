from aiogram.types import Message

from config import CHAT_GPT_TOKEN, CHAT_GPT_BASE_URL, CHAT_GPT_MODEL
from utils.gpt import GPT
from utils.help_load_res import load_prompt
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
