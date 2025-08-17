import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommandScopeDefault, MenuButtonCommands

from config import BOT_TOKEN, GPT_TOKEN, GPT_BASE_URL, GPT_MODEL, CHAT_GPT_TOKEN, CHAT_GPT_BASE_URL, CHAT_GPT_MODEL
from handlers import main_router
from middleware.injector_middleware import InjectorMiddleware
from middleware.typing_middleware import TypingMiddleware
from storage.factory import get_storage
from utils.gpt import GPT
from keyboards.all_kbs import set_commands
from utils.help_load_res import load_prompt
from utils.misc import on_start, on_shutdown


async def main() -> None:
    bot = Bot(token=BOT_TOKEN,
              default=DefaultBotProperties(
                  parse_mode=ParseMode.MARKDOWN
              )
              )
    storage = get_storage()
    gpt = GPT(
        gpt_key=GPT_TOKEN,
        model=GPT_MODEL,
        db=storage,
        base_prompt=load_prompt('base_prompt.txt'),
        base_url=GPT_BASE_URL,
        chat_gpt_key=CHAT_GPT_TOKEN,
        chat_gpt_base_url=CHAT_GPT_BASE_URL,
        chat_gpt_model=CHAT_GPT_MODEL
    )
    dp = Dispatcher(storage=storage)
    dp.update.middleware(InjectorMiddleware(gpt=gpt, storage=storage))
    dp.update.middleware(TypingMiddleware())

    dp.include_router(main_router)

    await bot.set_my_commands(
        commands=set_commands(),
        scope=BotCommandScopeDefault()
    )
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())

    await bot.delete_webhook(drop_pending_updates=True)

    dp.startup.register(on_start)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен Администратором")
