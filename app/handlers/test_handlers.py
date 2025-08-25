from aiogram import Router, Bot
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message
from datetime import datetime
from redis.asyncio import Redis


from config import REDIS_URL
from gpt.gpt import GPT
from keyboards.all_kbs import random_kb
from storage.abstract_storage import AbstractStorage
from utils.help_messages import escape_md, safe_markdown_answer, safe_markdown_edit

test_router = Router()


async def create_redis_pool() -> Redis:
    return Redis.from_url(REDIS_URL, decode_responses=True)


@test_router.message(Command('next'))
async def next_client(message: Message, gpt: GPT):
    gpt.manager.next_client()
    await message.answer(f'Установлен клтент: {gpt.manager.get_client().name}')

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

@test_router.message(Command('long'))
async def long(message: Message):
    length = message.text.split()[-1]
    if length.isdigit():
        n = int(length)
        text = "".join("1" for i in range(n))
        await safe_markdown_answer(message, text, reply_markup=random_kb())

@test_router.message(Command('ledit'))
async def ledit(message: Message):
    length = message.text.split()[-1]
    if length.isdigit():
        n = int(length)
        text = "".join("1" for i in range(n))
        edit_msg = await message.answer("test test test")
        await safe_markdown_edit(edit_msg, text, reply_markup=random_kb())