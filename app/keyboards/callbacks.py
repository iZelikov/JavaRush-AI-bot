from aiogram.filters.callback_data import CallbackData


class AttackData(CallbackData, prefix='AD'):
    name: str
    target: str


class DefenseData(CallbackData, prefix='DD'):
    name: str
    block1: str
    block2: str


class TalkData(CallbackData, prefix='TD'):
    name: str
    prompt_file: str
    image_file: str
