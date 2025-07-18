from importlib.resources import read_text

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from utils.helpers import load_text, send_photo

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    help_text = load_text('help.txt')
    await send_photo(message, 'chat-gopota.jpg')
    await message.answer(f'Превед, {message.from_user.first_name or "Медвед"}!')
    await  message.answer(help_text)

@router.message(Command('gpt'))
async def cmd_gpt(message: Message):
    await send_photo(message,'robots.jpg')
    await message.answer(f'Чат ГоПоТу пока не завезли :( Ждём ключ!')

@router.message(Command('img'))
async def cmd_img(message: Message):
    await send_photo(message,'mona-gopnik.jpg')
    await message.answer(f'Скинь пару фоток - братва заценит. Можно вместе с мобилой.')

@router.message(Command('quiz'))
async def cmd_quiz(message: Message):
    await send_photo(message,'univer.jpg')
    await message.answer(f'Вилкой в глаз или в JavaRush?! \nЭ-э-э... Типа мы с тебя спрашивать будем, а ты нам обоснуешь за шмот, ООП и международное положение, усёк?')

@router.message(Command('random'))
async def cmd_random(message: Message):
    await send_photo(message,'chat-gopota-landscape.jpg')
    await message.answer(f'А ты курсе, что каждые пять минут общения с телеграм-ботом сокращают жизнь на пять минут?')

@router.message(Command('resume'))
async def cmd_random(message: Message):
    await send_photo(message,'resume.jpg')
    await message.answer(f'Давай колись, сколько у тя классов образования? Сэм-восэм е? Или даж ПТУ закончил? Питона душить умеешь? Ну и отлично! Зашлём тя в Гугол заместо Жопса или Цукермана или как там его... О! Серёги Блина!')

@router.message(Command('sovet'))
async def cmd_random(message: Message):
    await send_photo(message,'robots.jpg')
    await message.answer(f'Думаешь, какую киношку вечерком под пивко заценить, но стремаешься зашквариться? Да ты не тушуйся! Спроси у братвы. Пацаны плохого не посоветуют.')

@router.message(Command('talk'))
async def cmd_random(message: Message):
    await send_photo(message,'robots.jpg')
    await message.answer(f'Присаживайся - поболтаем. Тут все пацаны в авторитете, не шестёрки какие. Выбирай любого.')

@router.message(Command('train'))
async def cmd_random(message: Message):
    await send_photo(message,'chat-gopota.jpg')
    await message.answer(f'Давай играть, кто больше слов на буржуйской фене сечёт! Не боись, на интерес играем, ну или на просто так.')

@router.message(Command('trans'))
async def cmd_random(message: Message):
    await send_photo(message,'univer.jpg')
    await message.answer(f'Это Дрон - он у нас полиглот... В хорошем смысле! Как глотнёт сорокоградусной, так начинает всякую туфту гнать не по нашему. Да ты сам проверь! Он и на китайском бакланит, и на эльфийском, и даж на клингонском!')