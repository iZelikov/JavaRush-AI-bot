from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.all_kbs import random_kb
from states.states import RandomFacts
from gpt.gpt import GPT
from utils.help_dialogs import clear_callback, save_message, clear_saved_message_kb, delete_saved_message, \
    get_saved_message
from utils.help_load_res import load_prompt
from utils.help_messages import safe_markdown_edit

random_fact_router = Router()


@random_fact_router.message(F.text, RandomFacts.next_fact)
async def random_fact(message: Message, gpt: GPT, state: FSMContext):
    await clear_saved_message_kb('random', state, message.bot)
    await message.answer(
        "Братан, я автомат по генерации бредовых фактов и не умею в дискуссии. Нажми на кнопку - получишь результат!",
        reply_markup=random_kb()
    )


@random_fact_router.callback_query(F.data == 'next_fact', RandomFacts.next_fact)
async def random_fact(callback: CallbackQuery, gpt: GPT, state: FSMContext):
    await clear_callback(callback)
    answer_message = await callback.message.answer('Вспоминает...')
    response = await gpt.dialog(
        callback,
        load_prompt('random_fact.txt'),
        text="Расскажи новый интересный факт",
        output_message=answer_message)
    await save_message('random', answer_message, state)
    await safe_markdown_edit(answer_message, response, reply_markup=random_kb())
