from aiogram.fsm.state import State, StatesGroup

class GPTDIalog(StatesGroup):
    active_dialog = State()

class ImageRecognition(StatesGroup):
    ready_to_accept = State()

class RandomFacts(StatesGroup):
    next_fact = State()

class Quiz(StatesGroup):
    select_theme = State()
    game = State()

class Resume(StatesGroup):
    profession = State()
    education = State()
    skills = State()
    experience = State()
    projects = State()
    final_edition = State()

class Sovet(StatesGroup):
    choose_entertainment = State()
    choose_genre = State()
    next_sovet = State()

class Talk(StatesGroup):
    choose_person = State()
    active_dialog = State()

class Trans(StatesGroup):
    translation = State()
