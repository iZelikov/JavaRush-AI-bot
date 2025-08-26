import json

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.all_kbs import genre_kb, entertain_kb
from states.states import Sovet
from storage.abstract_storage import AbstractStorage
from gpt.gpt import GPT
from utils.help_dialogs import clear_all, clear_callback
from utils.help_load_res import load_text
from utils.help_photo import send_photo
from utils.help_sovet import get_sovet

sovet_router = Router()


@sovet_router.callback_query(F.data == 'sovet_reset', StateFilter(*Sovet.__states__))
async def sovet_reset(callback: CallbackQuery, storage: AbstractStorage, state: FSMContext):
    await clear_all(callback, state, storage)
    await state.set_state(Sovet.choose_entertainment)
    await callback.message.delete()
    await send_photo(callback.message, 'company-tv.jpg')
    await callback.message.answer(load_text('command_sovet.txt', 1), reply_markup=entertain_kb())


@sovet_router.callback_query(Sovet.choose_entertainment)
async def choose_genre(callback: CallbackQuery, state: FSMContext):
    await clear_callback(callback)
    await state.set_state(Sovet.choose_genre)
    entertainments = json.loads(load_text("entertainments.json"))
    await callback.message.answer(entertainments[callback.data]['name'])
    await callback.message.answer("Выбери жанр развлекухи:", reply_markup=genre_kb(callback.data))
    await state.set_data({"entertain": callback.data})


@sovet_router.callback_query(Sovet.choose_genre)
async def next_sovet(callback: CallbackQuery, gpt: GPT, state: FSMContext):
    await clear_callback(callback)
    await state.set_state(Sovet.next_sovet)
    data = await state.get_data()
    entertain = data['entertain']
    genre = callback.data
    entertainments = json.loads(load_text("entertainments.json"))
    entertainment_name = entertainments[entertain]['name']
    genre_name = entertainments[entertain]['genres'][genre].split(' - ')[0]
    text = f"Хочу {entertainment_name}. Жанр - {genre_name}."
    await get_sovet(text, callback, gpt)


@sovet_router.callback_query(Sovet.next_sovet)
async def next_sovet(callback: CallbackQuery, gpt: GPT, state: FSMContext):
    await clear_callback(callback)
    await callback.message.delete()
    text = callback.data
    await get_sovet(text, callback, gpt)


@sovet_router.message(StateFilter(*Sovet.__states__))
async def wrong_message(message: Message, state: FSMContext):
    await message.answer('Тут говорить не надо, тут надо на кнопки жмакать!')
