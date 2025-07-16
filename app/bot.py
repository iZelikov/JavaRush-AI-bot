import asyncio
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from utils.random_msg import rnd_text

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()


# Command handler
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f'Превед! {rnd_text()}')

@dp.message(F.text)
async def common_text_handler(message: Message) -> None:
    await message.answer(f'Короче! {rnd_text()}')


# Run the bot
async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
