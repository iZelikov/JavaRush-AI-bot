from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import BotCommand
from utils.helpers import load_text

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
