import os
from random import choice

def rnd_text() -> str:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    with open(os.path.join(BASE_DIR, 'resources/texts/gopota.txt'), 'r' , encoding='utf8') as file:
        texts = file.read().split('\n')
        return choice(texts)
