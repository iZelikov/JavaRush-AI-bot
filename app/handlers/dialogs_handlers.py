from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from states.states import GPTDIalog
from storage.abstract_storage import AbstractStorage
from gpt.gpt import GPT
from utils.help_dialogs import clear_all, clear_callback
from utils.help_load_res import load_text, load_prompt
from utils.help_messages import safe_markdown_edit
from utils.help_photo import send_photo

dialog_router = Router()


@dialog_router.message(lambda message: message.sticker)
async def handle_sticker(message: Message):
    await message.answer("Смешно, братва заценила! Но ты не отвлекайся, пиши строго по делу!")


@dialog_router.callback_query(F.data == 'cancel_and_restart')
async def cancel_dialog(callback: CallbackQuery, gpt: GPT, state: FSMContext, storage: AbstractStorage):
    await clear_callback(callback)
    await send_photo(callback.message, 'chat-gopota.jpg')
    answer_message = await callback.message.answer('Подыскивает прощальные слова...')
    response_text = await gpt.dialog(
        callback,
        load_prompt('cancel.txt'), text="На сегодня хватит, мне пора идти",
        output_message=answer_message)
    await safe_markdown_edit(answer_message, response_text)
    help_text = load_text('help.txt')
    await callback.message.answer(help_text, reply_markup=ReplyKeyboardRemove())


@dialog_router.message(F.text, GPTDIalog.active_dialog)
async def gpt_dialog(message: Message, gpt: GPT):
    answer_message = await message.answer('Думает...')
    response_text = await gpt.dialog(
        message,
        load_prompt('gpt.txt'),
        output_message=answer_message)
    await safe_markdown_edit(answer_message, response_text)
