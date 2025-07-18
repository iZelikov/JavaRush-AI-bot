from aiogram.types import Message, FSInputFile

from config import BASE_DIR
from random import choice

def rnd_text() -> str:
    texts = load_text('gopota.txt').split('\n')
    return choice(texts)

def load_text(filename: str) -> str:
    text_filename = BASE_DIR / 'resources' / 'texts' / filename
    with open(text_filename, 'r' , encoding='utf8') as text_file:
        return text_file.read()

async def send_photo(message: Message, img_name: str):
    img_path = BASE_DIR / 'resources' / 'images' / img_name
    photo = FSInputFile(img_path)
    await message.answer_photo(photo=photo)

