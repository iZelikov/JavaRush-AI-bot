from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.all_kbs import langs_choosing_kb, trans_kb
from states.states import Trans
from utils.gpt import GPT
from utils.help_load_res import load_prompt
from utils.help_messages import safe_markdown_edit

trans_router = Router()



@trans_router.callback_query(Trans.translation, F.data == "other_lang")
async def other_language(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()
    await state.set_state(Trans.translation)
    await callback.message.answer("Выбери Язык:", reply_markup=langs_choosing_kb())


@trans_router.callback_query(Trans.translation)
async def set_language(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()
    lang = callback.data.split('_')[1]
    await state.set_data({'lang': lang})
    await callback.message.answer(f"Готов переводить на *{lang}*.\nШли маляву!")


@trans_router.message(F.text, Trans.translation)
async def translate(message: Message, gpt: GPT, state: FSMContext):
    data = await state.get_data()
    lang = data['lang']

    if "kb_message" in data:
        try:
            await message.bot.delete_message(
                chat_id=data["kb_message"]["chat_id"],
                message_id=data["kb_message"]["message_id"]
            )
        except Exception as e:
            print(f"Не удалось удалить сообщение: {e}")

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

    await state.update_data({
        "kb_message": {
            "message_id": kb_message.message_id,
            "chat_id": kb_message.chat.id
        }
    })