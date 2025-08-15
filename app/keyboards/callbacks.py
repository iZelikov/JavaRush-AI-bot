from aiogram.filters.callback_data import CallbackData


class TalkData(CallbackData, prefix='TD'):
    name: str
    prompt_file: str
    image_file: str
