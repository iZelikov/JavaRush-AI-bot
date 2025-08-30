from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from gpt.gpt import GPT
from keyboards.callbacks import DefenseData, AttackData
from states.states import GopStop
from utils.help_dialogs import clear_callback, delete_saved_message
from utils.help_gop_stop import start_fight, attack, defense, next_round, fight_description, win_description, \
    loose_description, draw_description

gop_stop_router = Router()


@gop_stop_router.message(StateFilter(*GopStop.__states__))
async def no_talk(message: Message):
    await message.answer('Время базара прошло! Сейчас говорят кулаки!')


@gop_stop_router.callback_query(GopStop.attack, F.data == 'fight')
async def first_attack(callback: CallbackQuery, state: FSMContext, gpt: GPT):
    await clear_callback(callback)
    await delete_saved_message('gop-stop', state, callback.bot)
    await start_fight(callback, state, gpt)


@gop_stop_router.callback_query(GopStop.attack, DefenseData.filter())
async def user_attack(callback: CallbackQuery, callback_data: DefenseData, state: FSMContext, gpt: GPT):
    await clear_callback(callback)
    fight = await next_round(callback, callback_data, state)
    result = fight.get('result')
    if result == 'fight':
        await fight_description(callback, fight.get("text", ""), gpt)
        await attack(callback, state)

    elif result == 'win':
        await win_description(callback, fight.get("text", ""), gpt)

    elif result == 'loose':
        await loose_description(callback, fight.get("text", ""), gpt)

    elif result == 'draw':
        await draw_description(callback, fight.get("text", ""), gpt)


@gop_stop_router.callback_query(GopStop.defense, AttackData.filter())
async def user_defense(callback: CallbackQuery, callback_data: AttackData, state: FSMContext):
    await clear_callback(callback)
    await defense(callback, state, callback_data)
