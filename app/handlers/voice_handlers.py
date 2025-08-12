from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from states.states import GPTDIalog
from utils.gpt import GPT
from utils.help_audio import message_audio_to_text, message_text_to_audio
from utils.help_load_res import load_prompt
from utils.help_messages import safe_markdown_edit

voice_router = Router()


@voice_router.message(Command('voice'))
async def cmd_voice(message: Message):
    text = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not text:
        await message.answer("⚠️ Напиши текст после команды /voice")
        return
    await message_text_to_audio(message, text)


@voice_router.message(lambda message: message.voice or message.audio, GPTDIalog.active_dialog)
async def gpt_audio_dialog(message: Message, gpt: GPT):
    recognized_text = await message_audio_to_text(message)
    if recognized_text:
        await message.reply(f"🎤 Говоришь:\n{recognized_text}")
        answer_message = await message.answer('Думает...')
        response_text = await gpt.dialog(
            message,
            load_prompt('gpt.txt'),
            text=recognized_text,
            bot_message=answer_message)
        await safe_markdown_edit(answer_message, response_text)
        temp_msg = await message.answer('Щас спою...')
        await message_text_to_audio(message, response_text.replace('*', ''))
        await temp_msg.delete()

    else:
        await message.reply(f"❌ Братан, ты чё-то сказал, а я ни черта не понял :(")


@voice_router.message(lambda message: message.voice or message.audio)
async def handle_audio_message(message: Message, gpt: GPT):
    recognized_text = await message_audio_to_text(message)
    if recognized_text:
        await message.reply(f"🎤 Говоришь:\n{recognized_text}")
        await message.answer("Иди с ГоПоТой побазарь, они такое любят! Жми /gpt - там тебе по понятиям всё разложат.")
    else:
        await message.reply(f"❌ Братан, ты чё-то сказал, а я ни черта не понял :(")
