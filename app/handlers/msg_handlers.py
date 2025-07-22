from aiogram import Router, F
from aiogram.enums import ChatAction
from aiogram.types import Message

from states.states import GPTDIalog
from utils.gpt import GPT
from utils.helpers import load_prompt

msg_router = Router()

@msg_router.message(F.text)
async def base_messages(message: Message, gpt: GPT):
    answer_message = await message.answer('думает...')
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    response = await gpt.ask_once(message, load_prompt('wait_command.txt'))
    await answer_message.edit_text(response)
