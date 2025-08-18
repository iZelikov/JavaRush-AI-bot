import json

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.all_kbs import genre_kb, user_prefer_kb, entertain_kb
from states.states import Sovet
from storage.abstract_storage import AbstractStorage
from utils.gpt import GPT
from utils.help_load_res import load_text, load_prompt
from utils.help_messages import safe_markdown_edit
from utils.help_photo import send_photo

sovet_router = Router()

@sovet_router.callback_query(F.data == 'sovet_reset', StateFilter(*Sovet.__states__))
async def sovet_reset(callback: CallbackQuery, storage: AbstractStorage, state: FSMContext):
    await state.clear()
    await state.set_state(Sovet.choose_entertainment)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()
    await storage.reset_history(callback.message.from_user.id)
    await send_photo(callback.message, 'company-tv.jpg')
    await callback.message.answer(load_text('command_sovet.txt', 1), reply_markup=entertain_kb())


@sovet_router.callback_query(Sovet.choose_entertainment)
async def choose_genre(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Sovet.choose_genre)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()
    entertainments = json.loads(load_text("entertainments.json"))
    await callback.message.answer(entertainments[callback.data]['name'])
    await callback.message.answer("Выбери жанр развлекухи:", reply_markup=genre_kb(callback.data))
    await state.set_data({"entertain": callback.data})


@sovet_router.callback_query(Sovet.choose_genre)
async def next_sovet(callback: CallbackQuery, gpt: GPT, state: FSMContext):
    await state.set_state(Sovet.next_sovet)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()
    data = await state.get_data()
    entertain = data['entertain']
    genre = callback.data
    entertainments = json.loads(load_text("entertainments.json"))
    entertainment_name = entertainments[entertain]['name']
    genre_name = entertainments[entertain]['genres'][genre].split(' - ')[0]
    text = f"Пользователь выбрал {entertainment_name}. Жанр - {genre_name}."
    await callback.message.answer(genre_name)
    answer_message = await callback.message.answer("ГоПоТа совещается...")
    response_text = await gpt.dialog(
        callback,
        load_prompt('sovet.txt'),
        text=text,
        output_message=answer_message)
    await safe_markdown_edit(answer_message, response_text)
    await callback.message.answer("Как тебе?", reply_markup=user_prefer_kb())


@sovet_router.callback_query(Sovet.next_sovet)
async def next_sovet(callback: CallbackQuery, gpt: GPT, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.delete()
    await callback.answer()
    text = callback.data
    await callback.message.answer(text)
    answer_message = await callback.message.answer("ГоПоТа совещается...")
    response_text = await gpt.dialog(
        callback,
        load_prompt('sovet.txt'),
        text=text,
        output_message=answer_message)
    await safe_markdown_edit(answer_message, response_text)
    await callback.message.answer("Как тебе?", reply_markup=user_prefer_kb())


@sovet_router.message(StateFilter(*Sovet.__states__))
async def wrong_message(message: Message, state: FSMContext):
    await message.answer('Тут говорить не надо, тут надо на кнопки жмакать!')