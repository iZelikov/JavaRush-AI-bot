import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommandScopeDefault, MenuButtonCommands

from config import BOT_TOKEN, GPT_TOKEN, GPT_BASE_URL, ENV
from handlers.cmd_handlers import cmd_router
from handlers.dialogs_handlers import dialog_router
from handlers.msg_handlers import msg_router
from handlers.test_handlers import test_router
from middleware.injector_middleware import InjectorMiddleware
from middleware.typing_middleware import TypingMiddleware
from storage.factory import get_storage
from utils.gpt import GPT
from keyboards.all_kbs import set_commands


async def main() -> None:
    bot = Bot(token=BOT_TOKEN,
              default=DefaultBotProperties(
                  parse_mode=ParseMode.MARKDOWN
              )
              )
    storage = get_storage()
    gpt = GPT(GPT_TOKEN, storage, GPT_BASE_URL)
    dp = Dispatcher(storage=storage)
    dp.update.middleware(InjectorMiddleware(gpt=gpt, storage=storage))
    dp.update.middleware(TypingMiddleware())

    if ENV == 'dev':
        dp.include_routers(test_router)

    dp.include_routers(cmd_router, dialog_router, msg_router)

    await bot.set_my_commands(
        commands=set_commands(),
        scope=BotCommandScopeDefault()
    )
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())

    await bot.delete_webhook(drop_pending_updates=True)

    print('Бот запущен')
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
