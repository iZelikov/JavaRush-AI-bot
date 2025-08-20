from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from utils import logger


async def log_user(message: Message, state: FSMContext):
    current_state = await state.get_state()
    user_id = message.from_user.id
    username = message.from_user.username
    fullname = message.from_user.full_name
    if current_state is None:
        logger.info(f"🟢 {fullname} ({username}: {user_id}) присоединился к нам")
    else:
        logger.info(f"🔄 {fullname} ({username}: {user_id}) вернулся из {current_state}")
