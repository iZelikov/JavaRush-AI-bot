import os
import uuid
import speech_recognition as sr
from aiogram.types import Message, FSInputFile
from gtts import gTTS
from pydub import AudioSegment
from pathlib import Path
from typing import Optional

from config import TEMP_DIR


def cleanup_temp_files(*file_paths: Path) -> None:
    """Удаляет временные файлы"""
    for file in file_paths:
        if file and file.exists():
            try:
                file.unlink()
            except OSError:
                pass


async def text_to_audio(text: str, lang: str = 'ru') -> Optional[Path]:
    """
    Преобразует текст в аудио (формат OGG)
    Возвращает пути к временным файлам (mp3_path, ogg_path)
    """
    try:
        unique_id = uuid.uuid4().hex
        mp3_path = TEMP_DIR / f"voice_{unique_id}.mp3"
        ogg_path = TEMP_DIR / f"voice_{unique_id}.ogg"

        # Генерация речи
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(str(mp3_path))

        # Конвертация в OGG
        audio = AudioSegment.from_mp3(str(mp3_path))
        audio.export(str(ogg_path), format="ogg")
        cleanup_temp_files(mp3_path)

        return ogg_path

    except Exception as e:
        print(f"Ошибка преобразования текста в аудио: {e}")
        return None


async def audio_to_text(audio_path: Path) -> Optional[str]:
    """Преобразует аудиофайл в текст"""
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(str(audio_path)) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data, language='ru-RU')

    except sr.UnknownValueError:
        print("Не удалось распознать речь")
        return None
    except sr.RequestError as e:
        print(f"Ошибка сервиса распознавания: {e}")
        return None
    except Exception as e:
        print(f"Неизвестная ошибка распознавания: {e}")
        return None


async def download_telegram_audio(
        file_id: str,
        bot,
        extension: str = "ogg"
) -> Optional[Path]:
    """Скачивает аудиофайл из Telegram и возвращает путь"""
    try:
        unique_id = uuid.uuid4().hex
        audio_path = TEMP_DIR / f"audio_{unique_id}.{extension}"

        file = await bot.get_file(file_id)
        await bot.download_file(file.file_path, str(audio_path))

        return audio_path

    except Exception as e:
        print(f"Ошибка скачивания файла: {e}")
        return None


async def convert_to_wav(audio_path: Path, extension: str) -> Path:
    """Конвертирует аудиофайл в WAV формат"""
    wav_path = audio_path.with_suffix('.wav')

    if extension != "wav":
        audio = AudioSegment.from_file(str(audio_path), format=extension)
        audio.export(str(wav_path), format="wav")
        return wav_path
    return audio_path


async def message_text_to_audio(message: Message, text: str = "") -> Optional[Path]:
    # Получаем текст из сообщения
    text = text or message.text

    # Преобразуем текст в аудио
    ogg_path = await text_to_audio(text)

    if ogg_path:
        await message.answer_voice(voice=FSInputFile(ogg_path))
    else:
        await message.reply("❌ Конвертировали, конвертировали, да не выконвертировали... Не получилось аудио, братан!")
    cleanup_temp_files(ogg_path)


async def message_audio_to_text(message: Message) -> Optional[str]:
    # Определяем параметры сообщения
    if message.voice:
        file_id = message.voice.file_id
        extension = "ogg"
    elif message.audio:
        file_id = message.audio.file_id
        extension = message.audio.mime_type.split("/")[-1]
    else:
        return None

    # Скачиваем аудиофайл
    audio_path = await download_telegram_audio(file_id, message.bot, extension)
    if not audio_path:
        await message.reply("❌ Чё-то аудио не качается, может оно битое, братан?")
        return None

    # Конвертируем в WAV при необходимости
    wav_path = await convert_to_wav(audio_path, extension)

    # Преобразуем в текст
    text = await audio_to_text(wav_path)

    # Удаляем временные файлы
    cleanup_temp_files(audio_path, wav_path)

    return text
