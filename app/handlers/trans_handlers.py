from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.all_kbs import langs_choosing_kb, trans_kb
from states.states import Trans
from utils.gpt import GPT
from utils.help_dialogs import clear_callback, delete_saved_message, save_message
from utils.help_load_res import load_prompt
from utils.help_messages import safe_markdown_edit

trans_router = Router()



@trans_router.callback_query(Trans.translation, F.data == "other_lang")
async def other_language(callback: CallbackQuery, state: FSMContext):
    await clear_callback(callback)
    await callback.message.delete()
    await state.set_state(Trans.translation)
    await callback.message.answer("Выбери Язык:", reply_markup=langs_choosing_kb())


@trans_router.callback_query(Trans.translation)
async def set_language(callback: CallbackQuery, state: FSMContext):
    await clear_callback(callback)
    await callback.message.delete()
    lang = callback.data.split('_')[1]
    await state.set_data({'lang': lang})
    await callback.message.answer(f"Готов переводить на *{lang}*.\nШли маляву!")




@trans_router.message(F.text, Trans.translation)
async def translate(message: Message, gpt: GPT, state: FSMContext):
    key = "translate_kb_message"
    await delete_saved_message(key, state, message.bot)
    lang = await get_lang(state)
    prompt = f'{load_prompt("trans.txt")}\n\nПереведи следующий текст на {lang}'
    answer_message = await message.answer(f'Переводит стрелки...')

    response_text = await gpt.ask_once(
        message,
        prompt=prompt,
        output_message=answer_message)

    await safe_markdown_edit(answer_message, response_text)

    kb_message = await message.answer(
        "Кидай ещё маляву или жми на кнопку!",
        reply_markup=trans_kb()
    )
    await save_message(key, kb_message, state)


async def get_lang(state:FSMContext):
    data = await state.get_data()
    lang = data.get('lang', "Английский")
    return lang