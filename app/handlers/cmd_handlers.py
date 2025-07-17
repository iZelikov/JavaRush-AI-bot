from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f'Превед, *{message.from_user.full_name or "Медвед"}*!')
