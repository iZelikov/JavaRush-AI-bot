from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from datetime import datetime
from redis.asyncio import Redis

from config import REDIS_URL, REDIS_DB
from utils.helpers import load_text, send_photo
from utils.storage_factory import get_history_storage


router = Router()
storage = get_history_storage()

async def create_redis_pool() -> Redis:
    return Redis.from_url(REDIS_URL, decode_responses=True)


@router.message(Command('test'))
async def cmd_test(message: Message):
    user_id = message.from_user.id
    history = await storage.get_history(user_id)
    history.append(f"{user_id} - {datetime.now().strftime('%H:%M:%S')}: Тест")
    await storage.save_history(user_id, history)
    await message.answer("\n".join(history))

@router.message(Command("redis"))
async def check_redis(message: Message):
    try:
        redis = await create_redis_pool()
        await redis.ping()
        await message.answer("✅ Redis подключен успешно!")
    except Exception as e:
        await message.answer(f"❌ Ошибка Redis: {str(e)}")