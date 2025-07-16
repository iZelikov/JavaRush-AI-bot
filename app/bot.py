import asyncio
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()


# Command handler
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Симки е?")


# Run the bot
async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
