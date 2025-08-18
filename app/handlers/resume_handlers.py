from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from states.states import Resume
from utils.gpt import GPT
from utils.help_load_res import load_prompt
from utils.help_messages import safe_markdown_edit
from utils.help_resume import next_question, final_question

resume_router = Router()


@resume_router.callback_query(StateFilter(*Resume.__states__), F.data == 'restart_resume')
async def new_resume(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(Resume.profession)
    await callback.message.answer('```Resume:\nМы начинаем резюме...\nДля чего?..\nДля кого?..```')
    await next_question(callback, state, 1)


@resume_router.callback_query(F.data == 'next_info', Resume.profession)
async def get_education(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Resume.education)
    await next_question(callback, state, 2)


@resume_router.callback_query(F.data == 'next_info', Resume.education)
async def get_skills(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Resume.skills)
    await next_question(callback, state, 3)


@resume_router.callback_query(F.data == 'next_info', Resume.skills)
async def get_experience(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Resume.experience)
    await next_question(callback, state, 4)


@resume_router.callback_query(F.data == 'next_info', Resume.experience)
async def get_projects(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Resume.projects)
    await next_question(callback, state, 5)


@resume_router.callback_query(F.data == 'next_info', Resume.projects)
async def get_final(callback: CallbackQuery, gpt: GPT, state: FSMContext):
    await state.set_state(Resume.final_edition)
    await final_question(callback, state, gpt, 6)


@resume_router.message(StateFilter(Resume.final_edition))
async def final(message: Message, gpt: GPT, state: FSMContext):
    data = await state.get_data()
    text = "\n".join(data['resume'])
    answer_message = await message.answer("Кручу, верчу, HR запутать хочу...")
    prompt = f'{load_prompt("resume.txt")}\n{text}'
    response_text = await gpt.dialog(
        message,
        prompt,
        output_message=answer_message)
    await safe_markdown_edit(answer_message, response_text)


@resume_router.message(StateFilter(*Resume.__states__))
async def accum_messages(message: Message, state: FSMContext):
    current_data = await state.get_data()
    current_data['resume'] += [message.text]
    await state.update_data(current_data)
