from aiogram import Router, F
from aiogram.types import Message

from utils.helpers import load_prompt
from storage.factory import create_storages
from utils.gpt import gpt

router = Router()
state_store, history_store = create_storages()


@router.message(F.text)
async def base_messages(message: Message):
    answer_message = await message.answer('думает...')
    response = await gpt.get_response(message, load_prompt('gpt.txt'))
    await answer_message.edit_text(response)
