import json

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from keyboards.all_kbs import random_kb, genre_kb, user_prefer_kb, entertain_kb, langs_choosing_kb, trans_kb
from keyboards.callbacks import TalkData
from states.states import ImageRecognition, RandomFacts, GPTDIalog, Quiz, Resume, Sovet, Talk, Trans
from storage.abstract_storage import AbstractStorage
from utils.gpt import GPT
from utils.help_messages import safe_markdown_edit, extract_image_urls, send_photo, recognize_photo
from utils.help_load_res import load_text, load_prompt
from utils.help_quiz import extract_answers, get_answers_keyboard, generate_quiz
from utils.help_resume import next_question, final_question

dialog_router = Router()


@dialog_router.message(lambda message: message.sticker)
async def handle_sticker(message: Message):
    await message.answer("Смешно, братва заценила! Но ты не отвлекайся, пиши строго по делу!")


@dialog_router.callback_query(F.data == 'cancel_and_restart')
async def cancel_dialog(callback: CallbackQuery, gpt: GPT, state: FSMContext, storage: AbstractStorage):
    await state.clear()
    await storage.reset_history(callback.message.from_user.id)
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await send_photo(callback.message, 'chat-gopota.jpg')
    answer_message = await callback.message.answer('Подыскивает прощальные слова...')
    response_text = await gpt.ask_once(
        callback,
        load_prompt('cancel.txt'), text="На сегодня хватит, мне пора идти",
        bot_message=answer_message)
    await safe_markdown_edit(answer_message, response_text)
    help_text = load_text('help.txt')
    await  callback.message.answer(help_text, reply_markup=ReplyKeyboardRemove())


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
        callback,
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
        callback,
        gpt,
        text=theme)


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
    await callback.message.answer('```Resume:\nМы начинаем резюме...\nДля чего?..\nДля кого?..```')
    await next_question(callback, state, 1)


@dialog_router.callback_query(F.data == 'next_info', Resume.profession)
async def get_education(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Resume.education)
    await next_question(callback, state, 2)


@dialog_router.callback_query(F.data == 'next_info', Resume.education)
async def get_skills(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Resume.skills)
    await next_question(callback, state, 3)


@dialog_router.callback_query(F.data == 'next_info', Resume.skills)
async def get_experience(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Resume.experience)
    await next_question(callback, state, 4)


@dialog_router.callback_query(F.data == 'next_info', Resume.experience)
async def get_projects(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Resume.projects)
    await next_question(callback, state, 5)


@dialog_router.callback_query(F.data == 'next_info', Resume.projects)
async def get_final(callback: CallbackQuery, gpt: GPT, state: FSMContext):
    await state.set_state(Resume.final_edition)
    await final_question(callback, state, gpt, 6)


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


@dialog_router.callback_query(F.data == 'sovet_reset')
async def sovet_reset(callback: CallbackQuery, storage: AbstractStorage, state: FSMContext):
    await state.clear()
    await state.set_state(Sovet.choose_entertainment)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()
    await storage.reset_history(callback.message.from_user.id)
    await send_photo(callback.message, 'company-tv.jpg')
    await callback.message.answer(load_text('command_sovet.txt', 1), reply_markup=entertain_kb())


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
    text = f"Пользователь выбрал {entertainment_name}. Жанр - {genre_name}."
    await callback.message.answer(genre_name)
    answer_message = await callback.message.answer("ГоПоТа совещается...")
    response_text = await gpt.dialog(
        callback,
        load_prompt('sovet.txt'),
        text=text,
        bot_message=answer_message)
    await safe_markdown_edit(answer_message, response_text)
    await callback.message.answer("Как тебе?", reply_markup=user_prefer_kb())


@dialog_router.callback_query(Sovet.next_sovet)
async def next_sovet(callback: CallbackQuery, gpt: GPT, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()
    await callback.answer()
    text = callback.data
    await callback.message.answer(text)
    answer_message = await callback.message.answer("ГоПоТа совещается...")
    response_text = await gpt.dialog(
        callback,
        load_prompt('sovet.txt'),
        text=text,
        bot_message=answer_message)
    await safe_markdown_edit(answer_message, response_text)
    await callback.message.answer("Как тебе?", reply_markup=user_prefer_kb())


@dialog_router.message(StateFilter(*Sovet.__states__))
async def wrong_message(message: Message, state: FSMContext):
    await message.answer('Тут говорить не надо, тут надо на кнопки жмакать!')


@dialog_router.callback_query(TalkData.filter(), Talk.active_dialog)
async def robot_dialog(callback: CallbackQuery, callback_data: TalkData, gpt: GPT, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()
    await send_photo(callback.message, callback_data.image_file)
    prompt = f"{load_prompt('base_talk.txt')}\n{load_prompt(callback_data.prompt_file)}"
    await state.set_data({'prompt': prompt, 'name': callback_data.name})
    answer_message = await callback.message.answer(f'{callback_data.name} думает...')
    response_text = await gpt.dialog(
        callback,
        prompt=prompt,
        text='start_dialog',
        bot_message=answer_message
    )
    await safe_markdown_edit(answer_message, response_text)


@dialog_router.message(Talk.active_dialog)
async def robot_dialog(message: Message, gpt: GPT, state: FSMContext):
    data = await state.get_data()
    prompt = data['prompt']
    name = data['name']
    answer_message = await message.answer(f'{name} думает...')
    response_text = await gpt.dialog(
        message,
        prompt=prompt,
        bot_message=answer_message)
    await safe_markdown_edit(answer_message, response_text)

@dialog_router.callback_query(Trans.translation, F.data == "other_lang")
async def other_language(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()
    await state.set_state(Trans.translation)
    await callback.message.answer("Выбери Язык:", reply_markup=langs_choosing_kb())

@dialog_router.callback_query(Trans.translation)
async def set_language(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()
    lang = callback.data.split('_')[1]
    await state.set_data({'lang': lang})
    await callback.message.answer(f"Готов переводить на *{lang}*.\nШли маляву!")


from aiogram.types import Message


@dialog_router.message(F.text, Trans.translation)
async def translate(message: Message, gpt: GPT, state: FSMContext):
    data = await state.get_data()
    lang = data['lang']

    if "kb_message" in data:
        try:
            await message.bot.delete_message(
                chat_id=data["kb_message"]["chat_id"],
                message_id=data["kb_message"]["message_id"]
            )
        except Exception as e:
            print(f"Не удалось удалить сообщение: {e}")

    prompt = f'{load_prompt("trans.txt")}\n\nПереведи следующий текст на {lang}'
    answer_message = await message.answer(f'Переводит стрелки...')

    response_text = await gpt.ask_once(
        message,
        prompt=prompt,
        bot_message=answer_message)

    await safe_markdown_edit(answer_message, response_text)

    kb_message = await message.answer(
        "Кидай ещё маляву или жми на кнопку!",
        reply_markup=trans_kb()
    )

    await state.update_data({
        "kb_message": {
            "message_id": kb_message.message_id,
            "chat_id": kb_message.chat.id
        }
    })