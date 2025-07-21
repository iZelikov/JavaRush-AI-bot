from aiogram.fsm.state import State, StatesGroup

class GPTDIalog(StatesGroup):
    active_dialog = State()

class ImageRecognition(StatesGroup):
    ready_to_accept = State()

class RandomFacts(StatesGroup):
    next_fact = State()