import re
from random import sample

from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from keyboards.all_kbs import get_keyboard
from utils.gpt import GPT
from utils.help_load_res import load_text, load_prompt
from utils.help_messages import safe_markdown_edit


def get_themes(number: int) -> list[str]:
    all_themes = load_text('quiz_themes.txt').split('\n')
    themes = sample(all_themes, k=number)
    return themes


def extract_answers(text: str) -> tuple[str, list[str]]:

    options = re.findall(r'{[1-4][^}]+}', text)
    cleaned_text = re.sub(r'{[1-4][^}]+}', '', text)
    cleaned_text = re.sub(r'(\s*\n\s*){2,}', '\n\n', cleaned_text)
    options = [op.strip('{}') for op in options]
    return cleaned_text, options


def get_answers_keyboard(options):
    return get_keyboard(options, 'reply', adjust='2 2')


def get_quiz_themes_keyboard(number: int):
    themes = get_themes(number)
    keyboard = get_keyboard(themes)
    return keyboard


async def generate_quiz(
        message: Message | CallbackQuery,
        gpt: GPT,
        text=''):
    if isinstance(message, CallbackQuery):
        reply_message = message.message
    else:
        reply_message = message
    answer_message = await reply_message.answer('Генерирует вопрос...')
    response_text = await gpt.dialog(
        message,
        load_prompt('quiz_question.txt'),
        output_message=answer_message,
        text=text)
    question_text, options = extract_answers(response_text)
    await safe_markdown_edit(answer_message, question_text)
    if options:
        await reply_message.answer(
            'Твой ответ:',
            reply_markup=get_answers_keyboard(options))
    else:
        await reply_message.answer(
            'Твой ответ:',
            reply_markup=ReplyKeyboardRemove())
