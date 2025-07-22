import asyncio

from aiogram import Router, F
import aiohttp
from aiogram.enums import ChatAction
from aiogram.types import Message

from states.states import ImageRecognition, RandomFacts, GPTDIalog, Quiz
from utils.gpt import GPT
from utils.helpers import load_prompt

dialog_router = Router()

@dialog_router.message(F.text, GPTDIalog.active_dialog)
async def gpt_dialog(message: Message, gpt: GPT):
    answer_message = await message.answer('думает...')
    response = await gpt.dialog(message, load_prompt('gpt.txt'))
    await answer_message.edit_text(response)

@dialog_router.message(F.photo, ImageRecognition.ready_to_accept)
async def handle_photo(message: Message, gpt: GPT):
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    file_path = file.file_path

    file_url = f"https://api.telegram.org/file/bot{message.bot.id}/{file_path}"

    # Временная затычка пока нет ключа...
    answer_message = await message.answer('рассматривает фото...')
    response = await gpt.ask_once(message, load_prompt('blind.txt'))
    await answer_message.edit_text(response)

    # Скачиваем фото
    # async with aiohttp.ClientSession() as session:
    #     async with session.get(file_url) as resp:
    #         image_bytes = await resp.read()

    # Отправляем в OpenAI GPT-4-Vision (пока нет ключа :(
    # await message.answer('Фото обрабатывается')
    # response_text = await gpt.ask_gpt_vision(image_bytes)
    # await message.answer(response_text)

@dialog_router.message(F.text, ImageRecognition.ready_to_accept)
async def handle_photo(message: Message, gpt: GPT):
    # Временная затычка пока нет ключа...
    answer_message = await message.answer('рассматривает фото...')
    response = await gpt.ask_once(message, load_prompt('blind.txt'))
    await answer_message.edit_text(response)


@dialog_router.message(F.text, RandomFacts.next_fact)
async def random_fact(message: Message, gpt: GPT):
    answer_message = await message.answer('вспоминает...')
    response = await gpt.ask_once(message, load_prompt('random_fact.txt'))
    await answer_message.edit_text(response)


@dialog_router.message(F.text, Quiz.game)
async def quiz(message: Message, gpt: GPT):
    answer_message = await message.answer('внимание, вопрос...')
    response = await gpt.dialog(message, load_prompt('quiz.txt'))
    await answer_message.edit_text(response)