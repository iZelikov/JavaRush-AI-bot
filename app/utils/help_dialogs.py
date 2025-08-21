from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from storage.abstract_storage import AbstractStorage
from utils import logger


async def clear_all(
        message: Message | CallbackQuery,
        state: FSMContext,
        storage: AbstractStorage
):
    if isinstance(message, CallbackQuery):
        await clear_callback(message)
        message = message.message
    await state.clear()
    await storage.reset_history(message.from_user.id)


async def clear_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)


async def save_message(key: str, message: Message, state: FSMContext):
    await state.update_data({
        key: {
            "message_id": message.message_id,
            "chat_id": message.chat.id,
            "text": message.text
        }
    })

async def get_saved_message(key: str, state: FSMContext):
    data = await state.get_data()
    message_data = data.get(key)
    if message_data:
        return message_data.get("chat_id"), message_data.get("message_id")
    return None, None


async def delete_saved_message(key: str, state: FSMContext, bot: Bot):
    chat_id, message_id = await get_saved_message(key, state)
    if chat_id and message_id:
        try:
            await bot.delete_message(
                chat_id=chat_id,
                message_id=message_id
            )
        except Exception as e:
            logger.exception(f"Не удалось удалить сообщение: {e}")


