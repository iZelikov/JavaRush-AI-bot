from aiogram import Router, Bot
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message
from datetime import datetime
from redis.asyncio import Redis


from config import REDIS_URL
from storage.abstract_storage import AbstractStorage
from utils.help_messages import escape_md

test_router = Router()


async def create_redis_pool() -> Redis:
    return Redis.from_url(REDIS_URL, decode_responses=True)


@test_router.message(Command('test'))
async def cmd_test(message: Message, storage: AbstractStorage):
    user_id = message.from_user.id
    bot_id = message.bot.id
    chat_id = message.chat.id
    key = StorageKey(bot_id,chat_id, user_id)
    history = await storage.get_history(user_id)
    state = await storage.get_state(key)
    history.append({
        "role": "assistant",
        "content": f"{user_id} - {datetime.now().strftime('%H:%M:%S')}: {state}"})
    await storage.save_history(user_id, history)
    await message.answer("\n".join(map(str, history)), parse_mode=None)

@test_router.message(Command('test_clear'))
async def cmd_clear(message: Message, storage:AbstractStorage):
    user_id = message.from_user.id
    await storage.reset_history(user_id)
    await message.answer(f'История переписки юзера {user_id} очищена!')

@test_router.message(Command("redis"))
async def check_redis(message: Message):
    try:
        redis = await create_redis_pool()
        await redis.ping()
        await message.answer("✅ Redis подключен успешно!")
    except Exception as e:
        await message.answer(f"❌ Ошибка Redis: {str(e)}")

@test_router.message(Command('mark'))
async def test_markdown(message: Message):
    mark = """
*Обрамление одинарными звёздочками - жирный текст*    
_Обрамление одинарными подчёркиванием - курсив_
__Обрамление двойным подчёркиванием - подчёркнутый текст__
`Обрамление апострофами - код или моноширинный текст`
~Обрамление одной тильдой - зачёркнутый текст~
```Обрамление тройными апострофами блок кода или выделенный блок текста```
||Обрамление двойными вертикальными чертами <скрытый текст для спойлеров>||
"""
    await message.answer(escape_md(mark), parse_mode=ParseMode.MARKDOWN_V2)