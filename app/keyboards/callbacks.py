from aiogram.filters.callback_data import CallbackData


class AttackData(CallbackData, prefix='AD'):
    name: str
    target: str


class DefenseData(CallbackData, prefix='DD'):
    bk1: str
    bv1: int
    bk2: str
    bv2: int


class TalkData(CallbackData, prefix='TD'):
    name: str
    prompt_file: str
    image_file: str
