import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommandScopeDefault, MenuButtonCommands

from config import BOT_TOKEN
from gpt.gpt import GPT
from handlers import main_router
from keyboards.all_kbs import set_commands
from middleware.injector_middleware import InjectorMiddleware
from middleware.typing_middleware import TypingMiddleware
from storage.factory import get_storage
from utils import logger
from utils.help_gpt_manager import manager, chat_gpt_manager
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
        manager,
        storage=storage,
        base_prompt=load_prompt('base_prompt.txt'),
        chat_gpt_clients_manager=chat_gpt_manager
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
        logger.info("Бот остановлен Администратором")
