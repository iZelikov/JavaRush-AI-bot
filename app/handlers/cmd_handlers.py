from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from utils.helpers import load_text, send_photo
from utils.storage_factory import get_history_storage

router = Router()
storage = get_history_storage()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await storage.reset_history(message.from_user.id)
    help_text = load_text('help.txt')
    await send_photo(message, 'chat-gopota.jpg')
    await message.answer(f'Превед, {message.from_user.first_name or "Медвед"}!')
    await  message.answer(help_text)


@router.message(Command('gpt'))
async def cmd_gpt(message: Message):
    await storage.reset_history(message.from_user.id)
    await send_photo(message, 'company.jpg')
    await message.answer(load_text('command_gpt.txt', 0))
    await message.answer(load_text('command_gpt.txt', 1))


@router.message(Command('img'))
async def cmd_img(message: Message):
    await storage.reset_history(message.from_user.id)
    await send_photo(message, 'mona-gopnik.jpg')
    await message.answer(load_text('command_img.txt'))


@router.message(Command('quiz'))
async def cmd_quiz(message: Message):
    await storage.reset_history(message.from_user.id)
    await send_photo(message, 'vilka.jpg')
    await message.answer(load_text('command_quiz.txt'))


@router.message(Command('random'))
async def cmd_random(message: Message):
    await storage.reset_history(message.from_user.id)
    await send_photo(message, 'random.jpg')
    await message.answer(load_text('command_random.txt'))


@router.message(Command('resume'))
async def cmd_resume(message: Message):
    await storage.reset_history(message.from_user.id)
    await send_photo(message, 'resume.jpg')
    await message.answer(load_text('command_resume.txt'))


@router.message(Command('sovet'))
async def cmd_sovet(message: Message):
    await storage.reset_history(message.from_user.id)
    await send_photo(message, 'company-tv.jpg')
    await message.answer(load_text('command_sovet.txt'))


@router.message(Command('talk'))
async def cmd_talk(message: Message):
    await storage.reset_history(message.from_user.id)
    await send_photo(message, 'robots.jpg')
    await message.answer(load_text('command_talk.txt'))


@router.message(Command('train'))
async def cmd_train(message: Message):
    await storage.reset_history(message.from_user.id)
    await send_photo(message, 'chat-gopota-landscape.jpg')
    await message.answer(load_text('command_train.txt'))


@router.message(Command('trans'))
async def cmd_trans(message: Message):
    await storage.reset_history(message.from_user.id)
    await send_photo(message, 'univer.jpg')
    await message.answer(load_text('command_trans.txt'))
