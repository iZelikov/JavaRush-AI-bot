from aiogram.types import CallbackQuery

from keyboards.all_kbs import user_prefer_kb
from gpt.gpt import GPT
from utils.help_load_res import load_prompt
from utils.help_messages import safe_markdown_edit


async def get_sovet(text: str, callback: CallbackQuery, gpt: GPT):
    await callback.message.answer(text)
    answer_message = await callback.message.answer("ГоПоТа совещается...")
    response_text = await gpt.dialog(
        callback,
        load_prompt('sovet.txt'),
        text=text,
        output_message=answer_message)
    await safe_markdown_edit(answer_message, response_text)
    await callback.message.answer("Как тебе?", reply_markup=user_prefer_kb())
