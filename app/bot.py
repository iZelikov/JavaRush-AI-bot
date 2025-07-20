import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommandScopeDefault, MenuButtonCommands

from config import BOT_TOKEN
from handlers import cmd_handlers, msg_handlers, test_handlers
from keyboards.all_kbs import set_commands

async def main() -> None:
    dp = Dispatcher()
    dp.include_routers(test_handlers.router)
    dp.include_routers(
        cmd_handlers.router,
        msg_handlers.router,
    )
    bot = Bot(token=BOT_TOKEN)

    # await bot.delete_my_commands(scope=None, language_code=None)
    await bot.set_my_commands(commands=set_commands(), scope=BotCommandScopeDefault())
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
