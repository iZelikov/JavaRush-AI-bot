from aiogram import Router, F, Bot
from aiogram.types import Message

from utils.gpt import GPT
from utils.helpers import load_prompt

msg_router = Router()

@msg_router.message(F.text)
async def base_messages(message: Message, gpt: GPT):
    answer_message = await message.answer('думает...')
    response = await gpt.get_response(message, load_prompt('gpt.txt'))
    await answer_message.edit_text(response)