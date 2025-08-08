from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, BotCommand
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from utils.help_load_res import load_text


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

def resume_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Дальше",
        callback_data="next_info")
    )
    builder.add(InlineKeyboardButton(
        text="Давай заново!",
        callback_data="restart_resume"
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
