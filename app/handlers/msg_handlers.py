from aiogram import Router, F
from aiogram.types import Message

router = Router()


@router.message(F.text)
async def base_messages(message: Message):
    await message.answer("Короче, Склифософский!")
