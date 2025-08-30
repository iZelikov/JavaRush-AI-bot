from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from keyboards.all_kbs import quiz_next_kb
from states.states import Quiz
from utils import logger
from gpt.gpt import GPT
from utils.help_dialogs import clear_callback, save_message, clear_saved_message_kb, delete_saved_message
from utils.help_messages import safe_markdown_edit
from utils.help_load_res import load_text, load_prompt
from utils.help_quiz import generate_quiz, get_quiz_themes_keyboard

dialog_router = Router()

quiz_router = Router()


@quiz_router.callback_query(Quiz.select_theme)
async def select_theme(callback: CallbackQuery, gpt: GPT, state: FSMContext):
    await clear_callback(callback)
    theme = f"Тема: *{callback.data.split('_')[1]}*"
    await callback.message.answer(theme)
    await state.set_state(Quiz.question)
    await generate_quiz(
        callback,
        gpt,
        text=theme)


@quiz_router.message(Quiz.select_theme)
async def select_theme(message: Message, gpt: GPT, state: FSMContext):
    await clear_saved_message_kb("kb_quiz_themes", state, message.bot)
    await state.set_state(Quiz.question)
    await generate_quiz(message, gpt)


@quiz_router.message(Quiz.question)
async def quiz_answer(message: Message, gpt: GPT, state: FSMContext):
    await state.set_state(Quiz.answer)
    await message.answer(
        'Ответ принят!',
        reply_markup=ReplyKeyboardRemove())
    answer_message = await message.answer('Внимание! Правильный ответ...')
    response_text = await gpt.dialog(
        message,
        load_prompt('quiz_answer.txt'),
        output_message=answer_message)
    await safe_markdown_edit(
        answer_message,
        response_text,
        reply_markup=quiz_next_kb())
    await save_message('quiz', answer_message, state)


@quiz_router.message(Quiz.answer)
async def quiz_answer(message: Message, gpt: GPT, state: FSMContext):
    await clear_saved_message_kb('quiz', state, message.bot)
    answer_message = await message.answer('Думает...')
    response_text = await gpt.dialog(
        message,
        load_prompt('quiz_answer.txt'),
        output_message=answer_message)
    await safe_markdown_edit(
        answer_message,
        response_text,
        reply_markup=quiz_next_kb())


@quiz_router.callback_query(Quiz.answer, F.data == 'next_question')
async def quiz_next(callback: CallbackQuery, gpt: GPT, state: FSMContext):
    await clear_callback(callback)
    await state.set_state(Quiz.question)
    await generate_quiz(
        callback,
        gpt,
        text="Давай ещё вопрос по той же теме")


@quiz_router.callback_query(Quiz.answer, F.data == 'new_theme')
async def quiz_new_theme(callback: CallbackQuery, gpt: GPT, state: FSMContext):
    await clear_callback(callback)
    await state.set_state(Quiz.select_theme)
    kb_message = await callback.message.answer(
        load_text('command_quiz.txt', 1),
        reply_markup=get_quiz_themes_keyboard(6))
    await state.update_data({
        "kb_message": {
            "message_id": kb_message.message_id,
            "chat_id": kb_message.chat.id
        }
    })
