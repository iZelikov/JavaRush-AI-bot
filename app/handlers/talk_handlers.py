from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.callbacks import TalkData
from states.states import Talk
from gpt.gpt import GPT
from utils.help_dialogs import clear_callback
from utils.help_load_res import load_prompt
from utils.help_messages import safe_markdown_edit
from utils.help_photo import send_photo

talk_router = Router()


@talk_router.callback_query(TalkData.filter(), Talk.active_dialog)
async def robot_dialog(callback: CallbackQuery, callback_data: TalkData, gpt: GPT, state: FSMContext):
    await clear_callback(callback)
    await send_photo(callback.message, callback_data.image_file)
    prompt = f"{load_prompt('base_talk.txt')}\n{load_prompt(callback_data.prompt_file)}"
    await state.set_data({'prompt': prompt, 'name': callback_data.name})
    answer_message = await callback.message.answer(f'{callback_data.name} думает...')
    response_text = await gpt.dialog(
        callback,
        prompt=prompt,
        text='start_dialog',
        output_message=answer_message
    )
    await safe_markdown_edit(answer_message, response_text)


@talk_router.message(Talk.active_dialog)
async def robot_dialog(message: Message, gpt: GPT, state: FSMContext):
    data = await state.get_data()
    prompt = data['prompt']
    name = data['name']
    answer_message = await message.answer(f'{name} думает...')
    response_text = await gpt.dialog(
        message,
        prompt=prompt,
        output_message=answer_message)
    await safe_markdown_edit(answer_message, response_text)
