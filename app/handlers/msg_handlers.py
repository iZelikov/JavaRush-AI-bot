from aiogram import Router, F
from aiogram.types import Message

from utils.helpers import rnd_text, load_prompt
from utils.storage_factory import get_history_storage
from utils.gpt import gpt

router = Router()
storage = get_history_storage()



@router.message(F.text)
async def base_messages(message: Message):
    response = await gpt.get_response(message, load_prompt('gpt.txt'))
    await message.answer(response)