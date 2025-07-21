from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from datetime import datetime
from redis.asyncio import Redis

from config import REDIS_URL
from storage.factory import create_storages


router = Router()
state_store, history_store = create_storages()

async def create_redis_pool() -> Redis:
    return Redis.from_url(REDIS_URL, decode_responses=True)


@router.message(Command('test'))
async def cmd_test(message: Message):
    user_id = message.from_user.id
    history = await history_store.get_history(user_id)
    history.append({
        "role": "assistant",
        "content": f"{user_id} - {datetime.now().strftime('%H:%M:%S')}: Тест"})
    await history_store.save_history(user_id, history)
    await message.answer("\n".join(map(str, history)))

@router.message(Command('test_clear'))
async def cmd_test(message: Message):
    user_id = message.from_user.id
    await history_store.reset_history(user_id)
    await message.answer(f'История переписки юзера {user_id} очищена!')

@router.message(Command("redis"))
async def check_redis(message: Message):
    try:
        redis = await create_redis_pool()
        await redis.ping()
        await message.answer("✅ Redis подключен успешно!")
    except Exception as e:
        await message.answer(f"❌ Ошибка Redis: {str(e)}")