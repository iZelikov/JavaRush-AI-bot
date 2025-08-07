from aiogram import Router, F
from aiogram.types import Message

from utils.gpt import GPT
from utils.help_load_res import load_prompt

msg_router = Router()

@msg_router.message(F.text)
async def base_messages(message: Message, gpt: GPT):
    answer_message = await message.answer('Думает...')
    response = await gpt.ask_once(message, load_prompt('wait_command.txt'))
    await answer_message.edit_text(response)
