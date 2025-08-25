from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from gpt.gpt import GPT
from utils.help_dialogs import clear_callback
from utils.help_load_res import load_prompt
from utils.help_messages import safe_markdown_edit

last_router = Router()


@last_router.callback_query()
async def wrong_callback(callback: CallbackQuery):
    await clear_callback(callback)

@last_router.message(F.photo)
async def wrong_image(message: Message, gpt: GPT):
    answer_message = await message.answer('Думает...')
    prompt = f"{load_prompt('gpt.txt')}\n{load_prompt('wrong_img.txt')}"
    response = await gpt.dialog(
        message,
        prompt,
        output_message=answer_message)
    await safe_markdown_edit(answer_message, response)


@last_router.message(F.text)
async def base_messages(message: Message, gpt: GPT):
    answer_message = await message.answer('Думает...')
    response = await gpt.ask_once(
        message,
        load_prompt('wait_command.txt'),
        output_message=answer_message)
    await safe_markdown_edit(answer_message, response)
