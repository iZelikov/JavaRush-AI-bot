from aiogram import Router, F
from aiogram.types import Message

from utils.gpt import GPT
from utils.help_load_res import load_prompt
from utils.help_messages import safe_markdown_edit

msg_router = Router()

@msg_router.message(F.photo)
async def gpt_dialog(message: Message, gpt: GPT):
    answer_message = await message.answer('Думает...')
    prompt = f"{load_prompt('gpt.txt')}\n{load_prompt('wrong_img.txt')}"
    response = await gpt.dialog(message, prompt)
    await safe_markdown_edit(answer_message, response)

@msg_router.message(F.text)
async def base_messages(message: Message, gpt: GPT):
    answer_message = await message.answer('Думает...')
    response = await gpt.ask_once(message, load_prompt('wait_command.txt'))
    await safe_markdown_edit(answer_message, response)
