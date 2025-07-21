from aiogram.fsm.state import State, StatesGroup

class GPTDIalog(StatesGroup):
    active_dialog = State()
