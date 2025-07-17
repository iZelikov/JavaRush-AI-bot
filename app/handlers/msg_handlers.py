from aiogram import Router, F
from aiogram.types import Message
from utils.random_msg import rnd_text

router = Router()


@router.message(F.text)
async def base_messages(message: Message):
    await message.answer(f"Короче, Склифософский! {rnd_text()}")
