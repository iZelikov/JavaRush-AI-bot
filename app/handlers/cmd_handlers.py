from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from gpt.gpt import GPT
from storage.abstract_storage import AbstractStorage
from states.states import GPTDIalog, ImageRecognition, RandomFacts, Quiz, Resume, Sovet, Talk, Trans, GopStop
from keyboards.all_kbs import random_kb, entertain_kb, robots_kb, start_resume, langs_choosing_kb
from utils.help_dialogs import clear_all, save_message
from utils.help_gop_stop import gop_stop
from utils.help_logging import log_user
from utils.help_quiz import get_quiz_themes_keyboard
from utils.help_messages import safe_markdown_answer
from utils.help_photo import send_photo
from utils.help_load_res import load_text

cmd_router = Router()


@cmd_router.message(CommandStart())
async def cmd_start(message: Message, storage: AbstractStorage, state: FSMContext):
    await log_user(message, state)
    await clear_all(message, state, storage)
    help_text = load_text('help.txt')
    await send_photo(message, 'chat-gopota.jpg')
    await safe_markdown_answer(
        message,
        f'Превед _*{message.from_user.first_name or "Медвед"}*_')
    await message.answer(help_text, reply_markup=ReplyKeyboardRemove())


@cmd_router.message(Command('gopstop'))
async def cmd_gop_stop(message: Message, storage: AbstractStorage, state: FSMContext, gpt: GPT):
    await clear_all(message, state, storage)
    await state.set_state(GopStop.attack)
    await send_photo(message, 'gop-stop.jpg')
    await message.answer(load_text('command_gopstop.txt', 0))
    await gop_stop(gpt, message, state)


@cmd_router.message(Command('gpt'))
async def cmd_gpt(message: Message, storage: AbstractStorage, state: FSMContext):
    await clear_all(message, state, storage)
    await state.set_state(GPTDIalog.active_dialog)
    await send_photo(message, 'company.jpg')
    await message.answer(load_text('command_gpt.txt', 0))
    await message.answer(load_text('command_gpt.txt', 1), reply_markup=ReplyKeyboardRemove())


@cmd_router.message(Command('img'))
async def cmd_img(message: Message, storage: AbstractStorage, state: FSMContext):
    await clear_all(message, state, storage)
    await state.set_state(ImageRecognition.ready_to_accept)
    await send_photo(message, 'mona-gopnik.jpg')
    await message.answer(load_text('command_img.txt'), reply_markup=ReplyKeyboardRemove())


@cmd_router.message(Command('quiz'))
async def cmd_quiz(message: Message, storage: AbstractStorage, state: FSMContext):
    await clear_all(message, state, storage)
    await state.set_state(Quiz.select_theme)
    await send_photo(message, 'vilka.jpg')
    await message.answer(
        load_text('command_quiz.txt', 0),
        reply_markup=ReplyKeyboardRemove())
    kb_message = await message.answer(
        load_text('command_quiz.txt', 1),
        reply_markup=get_quiz_themes_keyboard(6))
    await save_message("kb_quiz_themes", kb_message, state)


@cmd_router.message(Command('random'))
async def cmd_random(message: Message, storage: AbstractStorage, state: FSMContext):
    await clear_all(message, state, storage)
    await state.set_state(RandomFacts.next_fact)
    await send_photo(message, 'random.jpg')
    await message.answer(load_text('command_random.txt', 0), reply_markup=ReplyKeyboardRemove())
    kb = await message.answer(load_text('command_random.txt', 1), reply_markup=random_kb())
    await save_message('random', kb, state)


@cmd_router.message(Command('resume'))
async def cmd_resume(message: Message, storage: AbstractStorage, state: FSMContext):
    await clear_all(message, state, storage)
    await state.set_state(Resume.personal_data)
    await send_photo(message, 'resume.jpg')
    await message.answer(load_text('command_resume.txt'), reply_markup=ReplyKeyboardRemove())
    msg_text = load_text('resume.txt', 0)
    await message.answer(msg_text)
    await message.answer("*Готов поделиться персональными данными с братвой?*", reply_markup=start_resume())


@cmd_router.message(Command('sovet'))
async def cmd_sovet(message: Message, storage: AbstractStorage, state: FSMContext):
    await clear_all(message, state, storage)
    await state.set_state(Sovet.choose_entertainment)
    await send_photo(message, 'company-tv.jpg')
    await message.answer(load_text('command_sovet.txt'), reply_markup=ReplyKeyboardRemove())
    await message.answer(load_text('command_sovet.txt', 1), reply_markup=entertain_kb())


@cmd_router.message(Command('talk'))
async def cmd_talk(message: Message, storage: AbstractStorage, state: FSMContext):
    await clear_all(message, state, storage)
    await state.set_state(Talk.active_dialog)
    await send_photo(message, 'robots.jpg')
    await message.answer(load_text('command_talk.txt'), reply_markup=ReplyKeyboardRemove())
    await message.answer(load_text('command_talk.txt', 1), reply_markup=robots_kb())


@cmd_router.message(Command('train'))
async def cmd_train(message: Message, storage: AbstractStorage, state: FSMContext):
    await clear_all(message, state, storage)
    await send_photo(message, 'chat-gopota-landscape.jpg')
    await message.answer(load_text('command_train.txt'), reply_markup=ReplyKeyboardRemove())


@cmd_router.message(Command('trans'))
async def cmd_trans(message: Message, storage: AbstractStorage, state: FSMContext):
    await clear_all(message, state, storage)
    await state.set_state(Trans.translation)
    await send_photo(message, 'univer.jpg')
    await message.answer(load_text('command_trans.txt'), reply_markup=ReplyKeyboardRemove())
    await message.answer("Выбери Язык:", reply_markup=langs_choosing_kb())
