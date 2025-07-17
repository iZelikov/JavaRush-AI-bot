from config import BASE_DIR
from random import choice

def rnd_text() -> str:
    text_filename = BASE_DIR / 'resources' / 'texts' / 'gopota.txt'
    with open(text_filename, 'r' , encoding='utf8') as file:
        texts = file.read().split('\n')
        return choice(texts)
