import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from keyboards.all_kbs import random_kb, get_keyboard
from states.states import ImageRecognition, RandomFacts, GPTDIalog, Quiz
from storage.abstract_storage import AbstractStorage
from utils.gpt import GPT
from utils.help_messages import safe_markdown_edit, extract_image_urls, send_photo, recognize_photo
from utils.help_load_res import load_text, load_prompt

dialog_router = Router()


@dialog_router.callback_query(F.data == 'cancel_and_restart')
async def cancel_dialog(callback: CallbackQuery, gpt: GPT, state: FSMContext, storage: AbstractStorage):
    await state.clear()
    await storage.reset_history(callback.message.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()
    await send_photo(callback.message, 'chat-gopota.jpg')
    answer_message = await callback.message.answer('Подыскивает прощальные слова...')
    response_text = await gpt.ask_once(
        callback.message,
        load_prompt('cancel.txt'), text="На сегодня хватит, мне пора идти",
        bot_message=answer_message)
    await safe_markdown_edit(answer_message, response_text)
    help_text = load_text('help.txt')
    await  callback.message.answer(help_text)


@dialog_router.message(F.text, GPTDIalog.active_dialog)
async def gpt_dialog(message: Message, gpt: GPT):
    answer_message = await message.answer('Думает...')
    response_text = await gpt.dialog(
        message,
        load_prompt('gpt.txt'),
        bot_message=answer_message)
    await safe_markdown_edit(answer_message, response_text)


@dialog_router.message(F.photo, ImageRecognition.ready_to_accept)
async def handle_photo(message: Message, gpt: GPT):
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    img_path = file.file_path
    img_url = f"https://api.telegram.org/file/bot{message.bot.token}/{img_path}"
    await recognize_photo(file_url=img_url, message=message, gpt=gpt)


@dialog_router.message(F.text, ImageRecognition.ready_to_accept)
async def handle_photo(message: Message, gpt: GPT):
    urls = extract_image_urls(message)
    for img_url in urls:
        await message.answer_photo(img_url)
        await recognize_photo(file_url=img_url, message=message, gpt=gpt)


@dialog_router.message(F.text, RandomFacts.next_fact)
async def random_fact(message: Message, gpt: GPT):
    answer_message = await message.answer('Вспоминает...')
    response = await gpt.dialog(
        message,
        load_prompt('random_fact.txt'),
        bot_message=answer_message)
    await safe_markdown_edit(answer_message, response, reply_markup=random_kb())


@dialog_router.callback_query(F.data == 'next_fact', RandomFacts.next_fact)
async def random_fact(callback: CallbackQuery, gpt: GPT):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()
    answer_message = await callback.message.answer('Вспоминает...')
    response = await gpt.dialog(
        callback.message,
        load_prompt('random_fact.txt'),
        text="Расскажи новый интересный факт",
        bot_message=answer_message)
    await safe_markdown_edit(answer_message, response, reply_markup=random_kb())


@dialog_router.message(F.text, Quiz.game)
async def quiz(message: Message, gpt: GPT):
    answer_message = await message.answer('Генерирует вопрос...')
    response_text = await gpt.dialog(
        message,
        load_prompt('quiz.txt'),
        bot_message=answer_message)
    question_text, options = extract_answers(response_text)
    keyboard = get_keyboard(options, 'reply', adjust='2 2')
    await safe_markdown_edit(answer_message, question_text)
    if options:
        await message.answer('Твой ответ:', reply_markup=keyboard)
    else:
        await message.answer('Твой ответ:', reply_markup=ReplyKeyboardRemove())


def extract_answers(text):
    options = re.findall(r'\n(\d+\)[^\n]*)', text)
    options = list(map(str.strip, options))
    cleaned_text = re.sub(r'\n\s*\d+\)[^\n]*', '', text).strip()
    return cleaned_text, options
