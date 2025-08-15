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
    """
    Извлекаем варианты ответов из текста, сгенерированного GPT.

    Раньше тут было довольно простое и элегантное регулярное выражение, но из-за того, что GPT присылает что угодно, только не заданный шаблон, пришлось его долго и мучительно допиливать с подсказками искусственного интеллекта. В результате вот такой ужас из лучших мемов про вайб-кодинг. И всё равно бывают косяки :(

    :param text: str
    :return: cleaned_text: str, options: list[str]
    """
    # Шаг 1: Найти все позиции маркеров 1), 2), 3), 4)
    markers = []
    for match in re.finditer(r'(?<!\d)([1-4]\))(?!\d)', text):
        markers.append((match.group(1), match.start(), match.end()))

    # Если нет маркеров, возвращаем исходный текст
    if not markers:
        return text, []

    # Шаг 2: Извлечь текст между маркерами
    options = []
    for i in range(len(markers)):
        start = markers[i][2]  # конец текущего маркера
        if i < len(markers) - 1:
            end = markers[i + 1][1]  # начало следующего маркера
        else:
            # Для последнего варианта идем до конца строки
            end = text.find('\n', markers[i][1])
            if end == -1:
                end = len(text)

        option_text = text[start:end].strip()
        full_option = f"{markers[i][0]} {option_text}"
        options.append(full_option)

    # Как обычно, всё удаляется криво, так что пусть лучше остаются.
    # Шаг 3: Удалить варианты из текста
    # Создаем список диапазонов для удаления (от начала маркера до конца его текста)
    # remove_ranges = []
    # for i, (marker, start, end) in enumerate(markers):
    #     if i < len(markers) - 1:
    #         remove_end = markers[i + 1][1]  # до начала следующего маркера
    #     else:
    #         remove_end = end + len(options[i]) - len(marker)  # конец текста варианта
    #
    #     remove_ranges.append((start, remove_end))

    # Сортируем диапазоны в обратном порядке для безопасного удаления
    # remove_ranges.sort(reverse=True)
    # cleaned_text = text
    # for start, end in remove_ranges:
    #     cleaned_text = cleaned_text[:start] + cleaned_text[end:]

    # Убрать множественные пустые строки
    # cleaned_text = re.sub(r'(\n\s*){2,}', '\n\n', cleaned_text)

    return text, options


def get_answers_keyboard(options):
    return get_keyboard(options, 'reply', adjust='2 2')


def get_quiz_keyboard(number: int):
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
        load_prompt('quiz.txt'),
        bot_message=answer_message,
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
