import json
from random import randint, choice, random

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from gpt.gpt import GPT
from keyboards.all_kbs import attack_kb, defence_kb, gop_stop_kb, gop_stop_reload_kb
from keyboards.callbacks import AttackData, DefenseData
from states.states import GopStop
from utils.help_dialogs import save_message
from utils.help_load_res import load_text, load_prompt
from utils.help_messages import safe_markdown_edit
from utils.help_photo import send_photo


async def gop_stop(gpt: GPT, message: Message, state: FSMContext):
    answer_message = await message.answer("ГоПоТа недобро щурится...")
    response_text = await gpt.dialog(
        message,
        prompt=load_prompt('gop_stop.txt'),
        text='*пользователь заглядывает в тёмную подворотню в поисках приключений на свою ж*',
        output_message=answer_message)
    await safe_markdown_edit(answer_message, response_text)
    kb_msg = await message.answer(
        load_text('command_gopstop.txt', 1),
        reply_markup=gop_stop_kb()
    )
    await save_message('gop-stop', kb_msg, state)


async def start_fight(callback: CallbackQuery, state: FSMContext, gpt: GPT):
    await send_photo(callback.message, 'gop-stop-fight.jpg')
    await state.set_data({"fight": {"bot": {"hp": 100}, "user": {"hp": 100}}})
    await attack(callback, state)


async def attack(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Куда будешь бить?', reply_markup=attack_kb())
    await state.set_state(GopStop.defense)


async def defense(callback: CallbackQuery, state: FSMContext, callback_data: AttackData = None):
    if callback_data:
        await callback.message.edit_text(f"Атака *{callback_data.name.lower()}*")
        data = await state.get_data()
        data.get('fight').get('user')['attack'] = (callback_data.target, callback_data.name)
        await state.update_data(data)
    await callback.message.answer('Что защищать?', reply_markup=defence_kb())
    await state.set_state(GopStop.attack)


async def next_round(callback: CallbackQuery, callback_data: DefenseData | None, state: FSMContext):
    max_damage = 20
    min_damage = 10
    crit_chance = 0.3
    await callback.message.edit_text(f"Защищаю *{callback_data.name.lower()}*")
    data = await state.get_data()
    data.get('fight').get('user')['block'] = (callback_data.block1, callback_data.block2, callback_data.name)
    user_target = data.get('fight').get('user')['attack'][0]
    user_block = tuple(data.get('fight').get('user')['block'][:2])
    user_attack_text = f"Пользователь бьёт: {data.get('fight').get('user')['attack'][1]} ({user_target})"
    user_block_text = f"Пользователь защищает: {data.get('fight').get('user')['block'][2]} {user_block}"
    attack_json = json.loads(load_text('fight_attack_zones.json'))
    block_json = json.loads(load_text('fight_defense_zones.json'))
    bot_target = choice(list(attack_json.items()))[0]
    bot_block = tuple([list(zone.keys())[0] for zone in choice(list(block_json))])
    bot_attack_text = f"Ты бьёшь: {bot_target}"
    bot_block_text = f"Ты защищаешь: {bot_block}"
    user_crit = random() <= crit_chance
    bot_crit = random() <= crit_chance
    if bot_target in user_block:
        bot_damage = 0
        bot_damage_text = "Твой удар блокирован"
        if bot_crit:
            bot_damage = randint(min_damage, max_damage) // 2
            bot_damage_text = f"Ты пробиваешь блок критическим ударом на {bot_damage} hp"
    else:
        bot_damage = randint(min_damage, max_damage)
        bot_damage_text = f"Ты нанёс пользователю {bot_damage} hp урона"
        if bot_crit:
            bot_damage *= 2
            bot_damage_text = f"Ты нанёс пользователю {bot_damage} hp критического урона"
    user_hp = data.get('fight').get('user').get('hp') - bot_damage

    if user_target in bot_block:
        user_damage = 0
        user_damage_text = "Ты блокировал удар пользователя"
        if user_crit:
            user_damage = randint(min_damage, max_damage) // 2
            user_damage_text = f"Пользователь пробивает твой блок критическим ударом на {user_damage} hp"
    else:
        user_damage = randint(min_damage, max_damage)
        user_damage_text = f"Пользователь нанёс тебе {user_damage} hp урона"
        if user_crit:
            user_damage *= 2
            user_damage_text = f"Пользователь нанёс тебе {user_damage} hp критического урона"
    bot_hp = data.get('fight').get('bot').get('hp') - user_damage
    text = "\n".join((
        user_attack_text,
        user_block_text,
        bot_attack_text,
        bot_block_text,
        user_damage_text,
        bot_damage_text,
        f"Здоровье пользователя: {user_hp} hp",
        f"Твоё здоровье: {bot_hp} hp"
    ))
    # print(text)
    await state.update_data({"fight": {"bot": {"hp": bot_hp}, "user": {"hp": user_hp}}})
    if bot_hp <= 0 and user_hp <= 0:
        return {"text": text, "result": "draw"}
    elif bot_hp <= 0:
        return {"text": text, "result": "win"}
    elif user_hp <= 0:
        return {"text": text, "result": "loose"}
    else:
        return {"text": text, "result": "fight"}


async def fight_description(callback: CallbackQuery, text: str, gpt: GPT):
    answer_message = await callback.message.answer('Идёт махач...')
    response_text = await gpt.dialog(
        callback,
        prompt=load_prompt('gop_stop_fight.txt'),
        text=text,
        output_message=answer_message)
    await safe_markdown_edit(answer_message, response_text)


async def win_description(callback: CallbackQuery, text: str, gpt: GPT):
    await send_photo(callback.message,'gop-stop-win.jpg')
    text += load_prompt('gop_stop_win.txt')
    await fight_description(callback, text, gpt)
    kb_message = await callback.message.answer(
        "Ещё раунд?",
        reply_markup=gop_stop_reload_kb())


async def loose_description(callback: CallbackQuery, text: str, gpt: GPT):
    await send_photo(callback.message,'gop-stop-loose.jpg')
    text += load_prompt('gop_stop_loose.txt')
    await fight_description(callback, text, gpt)
    kb_message = await callback.message.answer(
        "Ещё раунд?",
        reply_markup=gop_stop_reload_kb())


async def draw_description(callback: CallbackQuery, text: str, gpt: GPT):
    await send_photo(callback.message,'gop-stop-draw.jpg')
    text += load_prompt('gop_stop_draw.txt')
    await fight_description(callback, text, gpt)
    kb_message = await callback.message.answer(
        "Ещё раунд?",
        reply_markup=gop_stop_reload_kb())
