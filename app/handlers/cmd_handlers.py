from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f'Превед, {message.from_user.first_name or "Медвед"}!')

@router.message(Command('gpt'))
async def cmd_gpt(message: Message):
    await message.answer(f'Чат ГоПоТу пока не завезли :( Ждём ключ!')