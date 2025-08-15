import json

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, BotCommand
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from config import BASE_DIR
from keyboards.callbacks import TalkData
from utils.help_load_res import load_text, load_prompt


def set_commands():
    txt_list = load_text('help.txt').split('\n')
    commands = [BotCommand(
        command=txt.split(' - ')[0][1:],
        description=txt.split(' - ')[1]
    ) for txt in txt_list]
    return commands


def main_kb():
    txt_list = load_text('help.txt').split('\n')
    kb_list = [[KeyboardButton(text=txt) for txt in txt_list]]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True)
    return keyboard


def random_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Ещё один факт",
        callback_data="next_fact")
    )
    builder.add(InlineKeyboardButton(
        text="Хватит",
        callback_data="cancel_and_restart"
    ))
    return builder.as_markup()


def start_resume():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Расскажу как на духу!',
        callback_data='restart_resume')
    builder.button(
        text='Фиг тебе, а не персональные данные!',
        callback_data="cancel_and_restart"
    )
    builder.adjust(1)
    return builder.as_markup()


def resume_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Дальше",
        callback_data="next_info")
    )
    builder.add(InlineKeyboardButton(
        text="Начать с начала",
        callback_data="restart_resume"
    ))
    return builder.as_markup()


def entertain_kb():
    entertainments = json.loads(load_text("entertainments.json"))
    builder = InlineKeyboardBuilder()
    for key, value in entertainments.items():
        builder.button(text=value['name'], callback_data=key)
    builder.adjust(1)
    return builder.as_markup()


def genre_kb(entertain):
    entertainments = json.loads(load_text("entertainments.json"))
    builder = InlineKeyboardBuilder()
    for key, value in entertainments[entertain]['genres'].items():
        builder.button(text=value, callback_data=key)
    builder.adjust(1)
    return builder.as_markup()


def user_prefer_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="✅ Ok",
        callback_data="✅ Нравится")
    )
    builder.add(InlineKeyboardButton(
        text="❌ Not Ok",
        callback_data="❌ Не нравится"
    ))
    builder.add(InlineKeyboardButton(
        text="🔄 Заново!",
        callback_data="sovet_reset"
    ))
    return builder.as_markup()


def get_keyboard(btn_names: list[str], keyboard_type: str = "inline", adjust: str = "1"):
    kb_adjust = map(int, adjust.split(' '))
    if keyboard_type == "inline":
        builder = InlineKeyboardBuilder()
        for button in btn_names:
            builder.button(text=button, callback_data=f"action_{button}")
        builder.adjust(*kb_adjust)
        return builder.as_markup()
    else:
        builder = ReplyKeyboardBuilder()
        for button in btn_names:
            builder.add(KeyboardButton(text=button))
        builder.adjust(*kb_adjust)
        return builder.as_markup(
            resize_keyboard=True,
            one_time_keyboard=True
        )


def robots_kb():
    prompt_dir = BASE_DIR / 'resources' / 'texts' / 'prompts'
    files = [file.name for file in prompt_dir.iterdir() if file.is_file() and file.name.startswith('talk_')]
    persons = []
    for name in files:
        text = load_prompt(name)
        persons.append(text[5: text.find('\n')])
    builder = InlineKeyboardBuilder()
    for button, filename in zip(persons, files):
        builder.button(text=button, callback_data=TalkData(
            name=button,
            prompt_file=filename,
            image_file=filename.replace('txt', 'jpg')
        ))
    builder.adjust(1)
    return builder.as_markup()


def langs_choosing_kb():
    langs = sorted(load_text('languages.txt').split())
    return get_keyboard(langs)


def trans_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Другой язык",
        callback_data="other_lang"
    )
    builder.button(
        text="Хватит",
        callback_data="cancel_and_restart"
    )
    return builder.as_markup()
