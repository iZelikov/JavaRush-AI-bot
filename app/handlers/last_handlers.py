from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from utils.gpt import GPT
from utils.help_load_res import load_prompt
from utils.help_messages import safe_markdown_edit

last_router = Router()


@last_router.callback_query()
async def wrong_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

@last_router.message(F.photo)
async def wrong_image(message: Message, gpt: GPT):
    answer_message = await message.answer('Думает...')
    prompt = f"{load_prompt('gpt.txt')}\n{load_prompt('wrong_img.txt')}"
    response = await gpt.dialog(
        message,
        prompt,
        bot_message=answer_message)
    await safe_markdown_edit(answer_message, response)


@last_router.message(F.text)
async def base_messages(message: Message, gpt: GPT):
    answer_message = await message.answer('Думает...')
    response = await gpt.ask_once(
        message,
        load_prompt('wait_command.txt'),
        bot_message=answer_message)
    await safe_markdown_edit(answer_message, response)
