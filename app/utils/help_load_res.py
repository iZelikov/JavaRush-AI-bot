import hashlib
from pathlib import Path
from random import choice

from aiogram.types import BufferedInputFile
from aiogram.utils.mypy_hacks import lru_cache

from config import BASE_DIR


@lru_cache(maxsize=256)
def load_text(filename: str | Path, fragment: int | None =0) -> str:
    text_filename = BASE_DIR / 'resources' / 'texts' / filename
    if fragment is None:
        return text_filename.read_text(encoding='utf-8')
    else:
        return text_filename.read_text(encoding='utf-8').split('\n\n')[fragment]


def rnd_text() -> str:
    texts = load_text('random_gopota.txt', fragment=None).split('\n\n')
    return choice(texts)


def load_sql(filename: str, fragment=0) -> str:
    sql_name = Path('sql', filename)
    return load_text(sql_name, fragment)


def load_prompt(filename: str) -> str:
    prompt_name = Path('prompts', filename)
    return load_text(prompt_name)


@lru_cache(maxsize=64)
def get_cached_photo(img_name: str) -> BufferedInputFile:
    img_path = BASE_DIR / 'resources' / 'images' / img_name
    if not img_path.exists():
        raise FileNotFoundError(f'Image {img_name} not found')
    img_bytes = img_path.read_bytes()
    file_hash = hashlib.md5(img_bytes).hexdigest()[:8]
    file_name = f"{img_path.stem}_{file_hash}{img_path.suffix}"
    return BufferedInputFile(img_bytes, filename=file_name)
