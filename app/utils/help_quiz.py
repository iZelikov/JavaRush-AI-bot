import re
from random import sample

from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.all_kbs import get_keyboard
from utils.gpt import GPT
from utils.help_load_res import load_text, load_prompt
from utils.help_messages import safe_markdown_edit


def get_themes(number: int) -> list[str]:
    all_themes = load_text('quiz_themes.txt').split('\n')
    themes = sample(all_themes, k=number)
    return themes


def extract_answers(text):
    raw_options = re.findall(r'\D([1-4]\)[^\n]*)', text)
    options = []
    for opt in raw_options:
        split_options = re.split(r'\D(?=[1-4]\))', opt)
        options.extend([o.strip() for o in split_options if o.strip()])
    cleaned_text = re.sub(r'\D([1-4]\)[^\n]*)', '', text)
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text).strip()
    return cleaned_text, options


def get_answers_keyboard(options):
    return get_keyboard(options, 'reply', adjust='2 2')


def get_quiz_keyboard(number: int):
    themes = get_themes(number)
    keyboard = get_keyboard(themes)
    return keyboard


async def generate_quiz(
        message: Message,
        gpt: GPT,
        text='',
        user_id: int = None):
    if user_id is None:
        user_id = message.from_user.id

    answer_message = await message.answer('Генерирует вопрос...')
    response_text = await gpt.dialog(
        message,
        load_prompt('quiz.txt'),
        bot_message=answer_message,
        text=text,
        user_id=user_id)
    question_text, options = extract_answers(response_text)
    await safe_markdown_edit(answer_message, question_text)
    if options:
        await message.answer(
            'Твой ответ:',
            reply_markup=get_answers_keyboard(options))
    else:
        await message.answer(
            'Твой ответ:',
            reply_markup=ReplyKeyboardRemove())
