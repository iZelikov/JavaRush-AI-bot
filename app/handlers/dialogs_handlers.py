import asyncio

from aiogram import Router, F
import aiohttp
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.all_kbs import random_kb
from states.states import ImageRecognition, RandomFacts, GPTDIalog, Quiz
from storage.abstract_storage import AbstractStorage
from utils.gpt import GPT
from utils.helpers import load_prompt, load_text, send_photo, safe_markdown_edit

dialog_router = Router()


@dialog_router.callback_query(F.data == 'cancel_and_restart')
async def cancel_dialog(callback: CallbackQuery, gpt: GPT, state: FSMContext, storage: AbstractStorage):
    await state.clear()
    await storage.reset_history(callback.message.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()
    await send_photo(callback.message, 'chat-gopota.jpg')
    answer_message = await callback.message.answer('Подыскивает прощальные слова...')
    response = await gpt.ask_once(callback.message, load_prompt('cancel.txt'), text="На сегодня хватит, мне пора идти")
    await safe_markdown_edit(answer_message, response)
    help_text = load_text('help.txt')
    await  callback.message.answer(help_text)


@dialog_router.message(F.text, GPTDIalog.active_dialog)
async def gpt_dialog(message: Message, gpt: GPT):
    answer_message = await message.answer('Думает...')
    response = await gpt.dialog(message, load_prompt('gpt.txt'))
    # await safe_markdown_edit(answer_message, response)
    await safe_markdown_edit(answer_message, response)


@dialog_router.message(F.photo, ImageRecognition.ready_to_accept)
async def handle_photo(message: Message, gpt: GPT):
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    file_path = file.file_path

    file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file_path}"
    answer_message = await message.answer('Рассматривает фото...')
    img_response = await gpt.ask_image(file_url, prompt=load_prompt("image_recognition.txt"))
    await answer_message.edit_text('Думает, чего бы умного сказать...')
    text_response = await gpt.ask_once(message, prompt=load_prompt("blind.txt"), text=img_response)
    await answer_message.edit_text(text_response)


@dialog_router.message(F.text, ImageRecognition.ready_to_accept)
async def handle_photo(message: Message, gpt: GPT):
    # Временная затычка пока нет ключа...
    answer_message = await message.answer('Рассматривает фото...')
    response = await gpt.ask_once(message, load_prompt('blind.txt'))
    await safe_markdown_edit(answer_message, response)


@dialog_router.message(F.text, RandomFacts.next_fact)
async def random_fact(message: Message, gpt: GPT):
    answer_message = await message.answer('Вспоминает...')
    response = await gpt.dialog(message, load_prompt('random_fact.txt'))
    await safe_markdown_edit(answer_message, response, reply_markup=random_kb())


@dialog_router.callback_query(F.data == 'next_fact', RandomFacts.next_fact)
async def random_fact(callback: CallbackQuery, gpt: GPT):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()
    answer_message = await callback.message.answer('Вспоминает...')
    response = await gpt.dialog(callback.message, load_prompt('random_fact.txt'), text="Давай ещё факт")
    await safe_markdown_edit(answer_message, response, reply_markup=random_kb())


@dialog_router.message(F.text, Quiz.game)
async def quiz(message: Message, gpt: GPT):
    answer_message = await message.answer('Генерирует вопрос...')
    response = await gpt.dialog(message, load_prompt('quiz.txt'))
    await safe_markdown_edit(answer_message, response)
