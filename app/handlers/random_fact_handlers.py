from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.all_kbs import random_kb
from states.states import RandomFacts
from utils.gpt import GPT
from utils.help_load_res import load_prompt
from utils.help_messages import safe_markdown_edit

random_fact_router = Router()


@random_fact_router.message(F.text, RandomFacts.next_fact)
async def random_fact(message: Message, gpt: GPT):
    answer_message = await message.answer('Вспоминает...')
    response = await gpt.dialog(
        message,
        load_prompt('random_fact.txt'),
        output_message=answer_message)
    await safe_markdown_edit(answer_message, response, reply_markup=random_kb())


@random_fact_router.callback_query(F.data == 'next_fact', RandomFacts.next_fact)
async def random_fact(callback: CallbackQuery, gpt: GPT):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()
    answer_message = await callback.message.answer('Вспоминает...')
    response = await gpt.dialog(
        callback,
        load_prompt('random_fact.txt'),
        text="Расскажи новый интересный факт",
        output_message=answer_message)
    await safe_markdown_edit(answer_message, response, reply_markup=random_kb())
