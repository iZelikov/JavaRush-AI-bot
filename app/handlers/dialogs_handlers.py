import json

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from keyboards.all_kbs import random_kb, get_keyboard, resume_kb, genre_kb, user_prefer_kb
from states.states import ImageRecognition, RandomFacts, GPTDIalog, Quiz, Resume, Sovet
from storage.abstract_storage import AbstractStorage
from utils.gpt import GPT
from utils.help_messages import safe_markdown_edit, extract_image_urls, send_photo, recognize_photo
from utils.help_load_res import load_text, load_prompt
from utils.help_quiz import extract_answers, get_answers_keyboard, generate_quiz
from utils.help_resume import next_question, final_question

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


@dialog_router.callback_query(Quiz.select_theme)
async def select_theme(callback: CallbackQuery, gpt: GPT, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()
    theme = f"Тема: *{callback.data.split('_')[1]}*"
    await callback.message.answer(theme)
    await state.set_state(Quiz.game)
    await generate_quiz(
        callback.message,
        gpt,
        text=theme,
        user_id=callback.from_user.id
    )


@dialog_router.message(Quiz.select_theme)
async def select_theme(message: Message, gpt: GPT, state: FSMContext):
    await state.set_state(Quiz.game)
    await generate_quiz(message, gpt)


@dialog_router.message(Quiz.game)
async def quiz(message: Message, gpt: GPT):
    temp_msg = await message.answer(
        'Принято!',
        reply_markup=ReplyKeyboardRemove())
    await temp_msg.delete()
    answer_message = await message.answer('Генерирует вопрос...')
    response_text = await gpt.dialog(
        message,
        load_prompt('quiz.txt'),
        bot_message=answer_message)
    question_text, options = extract_answers(response_text)
    await safe_markdown_edit(answer_message, question_text)
    if options:
        await message.answer(
            'Твой ответ:',
            reply_markup=get_answers_keyboard(options))
    else:
        await message.answer(
            'Твой ответ:',
            reply_markup=ReplyKeyboardRemove())


@dialog_router.callback_query(F.data == 'restart_resume')
async def new_resume(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(Resume.profession)
    await send_photo(callback.message, 'resume.jpg')
    await callback.message.answer('Погнали заново!')
    await next_question(callback.message, state, 1, callback)


@dialog_router.callback_query(F.data == 'next_info', Resume.profession)
async def get_education(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Resume.education)
    await next_question(callback.message, state, 2, callback)


@dialog_router.callback_query(F.data == 'next_info', Resume.education)
async def get_skills(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Resume.skills)
    await next_question(callback.message, state, 3, callback)


@dialog_router.callback_query(F.data == 'next_info', Resume.skills)
async def get_experience(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Resume.experience)
    await next_question(callback.message, state, 4, callback)


@dialog_router.callback_query(F.data == 'next_info', Resume.experience)
async def get_projects(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Resume.projects)
    await next_question(callback.message, state, 5, callback)


@dialog_router.callback_query(F.data == 'next_info', Resume.projects)
async def get_final(callback: CallbackQuery, gpt: GPT, state: FSMContext):
    await state.set_state(Resume.final_edition)
    await final_question(callback.message, state, gpt, 6, callback)


@dialog_router.message(StateFilter(Resume.final_edition))
async def final(message: Message, gpt: GPT, state: FSMContext):
    data = await state.get_data()
    text = "\n".join(data['resume'])
    answer_message = await message.answer("Кручу, верчу, HR запутать хочу...")
    prompt = f'{load_prompt("resume.txt")}\n{text}'
    response_text = await gpt.dialog(
        message,
        prompt,
        bot_message=answer_message)
    await safe_markdown_edit(answer_message, response_text)


@dialog_router.message(StateFilter(*Resume.__states__))
async def accum_messages(message: Message, state: FSMContext):
    current_data = await state.get_data()
    current_data['resume'] += [message.text]
    await state.update_data(current_data)


@dialog_router.callback_query(Sovet.choose_entertainment)
async def choose_genre(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Sovet.choose_genre)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()
    entertainments = json.loads(load_text("entertainments.json"))
    await callback.message.answer(entertainments[callback.data]['name'])
    await callback.message.answer("Выбери жанр развлекухи:", reply_markup=genre_kb(callback.data))
    await state.set_data({"entertain": callback.data})


@dialog_router.callback_query(Sovet.choose_genre)
async def next_sovet(callback: CallbackQuery, gpt: GPT, state: FSMContext):
    await state.set_state(Sovet.next_sovet)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()
    data = await state.get_data()
    entertain = data['entertain']
    genre = callback.data
    entertainments = json.loads(load_text("entertainments.json"))
    entertainment_name = entertainments[entertain]['name']
    genre_name = entertainments[entertain]['genres'][genre].split(' - ')[0]
    text = f"Пользователь выбрал {entertainment_name} жанра {genre_name}"
    await callback.message.answer(genre_name)
    answer_message = await callback.message.answer("Гопота совещается...")
    response_text = await gpt.dialog(
        callback.message,
        load_prompt('sovet.txt'),
        text=text,
        bot_message=answer_message)
    await safe_markdown_edit(answer_message, response_text)
    await callback.message.answer("Ну как тебе?", reply_markup=user_prefer_kb())


@dialog_router.callback_query(Sovet.next_sovet)
async def next_sovet(callback: CallbackQuery, gpt: GPT, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()
    await callback.answer()
    text = callback.data
    await callback.message.answer(text)
    answer_message = await callback.message.answer("Гопота совещается...")
    response_text = await gpt.dialog(
        callback.message,
        load_prompt('sovet.txt'),
        text=text,
        bot_message=answer_message)
    await safe_markdown_edit(answer_message, response_text)
    await callback.message.answer("Как тебе?", reply_markup=user_prefer_kb())


@dialog_router.message(StateFilter(*Sovet.__states__))
async def wrong_message(message: Message, state: FSMContext):
    await message.answer('Тут говорить не надо, тут надо на кнопки жмакать!')