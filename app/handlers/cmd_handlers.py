from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from states.states import GPTDIalog
from storage.abstract_storage import AbstractStorage
from utils.helpers import load_text, send_photo

cmd_router = Router()


@cmd_router.message(CommandStart())
async def cmd_start(message: Message, storage:AbstractStorage, state: FSMContext):
    await state.clear()
    await storage.reset_history(message.from_user.id)
    help_text = load_text('help.txt')
    await send_photo(message, 'chat-gopota.jpg')
    await message.answer(f'Превед, {message.from_user.first_name or "Медвед"}!')
    await  message.answer(help_text)


@cmd_router.message(Command('gpt'))
async def cmd_gpt(message: Message, storage:AbstractStorage, state: FSMContext):
    await state.clear()
    await state.set_state(GPTDIalog.active_dialog)
    await storage.reset_history(message.from_user.id)
    await send_photo(message, 'company.jpg')
    await message.answer(load_text('command_gpt.txt', 0))
    await message.answer(load_text('command_gpt.txt', 1))


@cmd_router.message(Command('img'))
async def cmd_img(message: Message, storage:AbstractStorage):
    await storage.reset_history(message.from_user.id)
    await send_photo(message, 'mona-gopnik.jpg')
    await message.answer(load_text('command_img.txt'))


@cmd_router.message(Command('quiz'))
async def cmd_quiz(message: Message, storage:AbstractStorage):
    await storage.reset_history(message.from_user.id)
    await send_photo(message, 'vilka.jpg')
    await message.answer(load_text('command_quiz.txt'))


@cmd_router.message(Command('random'))
async def cmd_random(message: Message, storage:AbstractStorage):
    await storage.reset_history(message.from_user.id)
    await send_photo(message, 'random.jpg')
    await message.answer(load_text('command_random.txt'))


@cmd_router.message(Command('resume'))
async def cmd_resume(message: Message, storage:AbstractStorage):
    await storage.reset_history(message.from_user.id)
    await send_photo(message, 'resume.jpg')
    await message.answer(load_text('command_resume.txt'))


@cmd_router.message(Command('sovet'))
async def cmd_sovet(message: Message, storage:AbstractStorage):
    await storage.reset_history(message.from_user.id)
    await send_photo(message, 'company-tv.jpg')
    await message.answer(load_text('command_sovet.txt'))


@cmd_router.message(Command('talk'))
async def cmd_talk(message: Message, storage:AbstractStorage):
    await storage.reset_history(message.from_user.id)
    await send_photo(message, 'robots.jpg')
    await message.answer(load_text('command_talk.txt'))


@cmd_router.message(Command('train'))
async def cmd_train(message: Message, storage:AbstractStorage):
    await storage.reset_history(message.from_user.id)
    await send_photo(message, 'chat-gopota-landscape.jpg')
    await message.answer(load_text('command_train.txt'))


@cmd_router.message(Command('trans'))
async def cmd_trans(message: Message, storage:AbstractStorage):
    await storage.reset_history(message.from_user.id)
    await send_photo(message, 'univer.jpg')
    await message.answer(load_text('command_trans.txt'))
