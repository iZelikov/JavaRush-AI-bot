from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.all_kbs import resume_kb
from utils.gpt import GPT
from utils.help_load_res import load_text, load_prompt
from utils.help_messages import safe_markdown_edit


async def next_question(
        callback: CallbackQuery,
        state: FSMContext,
        question: int = 0, ):
    resume_key = 'resume'
    question = load_text('resume.txt', question)
    if callback:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.answer()
        await callback.message.answer(question, reply_markup=resume_kb())
    data = await state.get_data()
    if not data:
        await state.set_data({resume_key: [f'system:\n{question}\n\nuser:']})
    else:
        data[resume_key] += [f'\nsystem:\n{question}\n\nuser:']
        await state.update_data(data)


async def final_question(
        callback: CallbackQuery,
        state: FSMContext,
        gpt: GPT,
        question: int = 0, ):
    resume_key = 'resume'
    if callback:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.answer()
        await callback.message.answer(load_text('resume.txt', question))
    data = await state.get_data()
    text = "\n".join(data[resume_key])
    answer_message = await callback.message.answer("Кручу, верчу, HR запутать хочу...")
    prompt = load_prompt("resume.txt")
    response_text = await gpt.dialog(
        callback,
        prompt,
        text=text,
        bot_message=answer_message)
    await safe_markdown_edit(answer_message, response_text)
