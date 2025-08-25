from aiogram import Router, F
from aiogram.types import Message

from states.states import ImageRecognition
from gpt.gpt import GPT
from utils.help_photo import recognize_photo, extract_image_urls

photo_router = Router()


@photo_router.message(F.photo, ImageRecognition.ready_to_accept)
async def handle_photo(message: Message, gpt: GPT):
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    img_path = file.file_path
    img_url = f"https://api.telegram.org/file/bot{message.bot.token}/{img_path}"
    await recognize_photo(file_url=img_url, message=message, gpt=gpt)


@photo_router.message(F.text, ImageRecognition.ready_to_accept)
async def handle_photo(message: Message, gpt: GPT):
    urls = extract_image_urls(message)
    for img_url in urls:
        await message.answer_photo(img_url)
        await recognize_photo(file_url=img_url, message=message, gpt=gpt)