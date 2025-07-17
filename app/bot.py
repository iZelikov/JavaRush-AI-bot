import asyncio
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers import cmd_handlers, msg_handlers


async def main() -> None:
    dp = Dispatcher()
    dp.include_routers(cmd_handlers.router, msg_handlers.router)
    bot = Bot(token=BOT_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
