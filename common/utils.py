from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery


async def generate_dates():
    """
    Generate next 12 days for appointment
    """
    today = datetime.now()
    dates = [(today + timedelta(days=i)).strftime('%d.%m') for i in range(12)][1:]
    return dates


async def get_dict_from_data(state, message, name_string):
    data = await state.get_data()
    title = data.get(f"{name_string}")
    description = message.text
    data = {"title": title, "description": description}
    return data


async def send_and_store_message(callback: CallbackQuery, message_text: str, reply_markup, state: FSMContext):
    msg = await callback.message.edit_text(message_text, reply_markup=reply_markup)
    await state.update_data(stored_message_id=msg.message_id, stored_chat_id=msg.chat.id)


async def delete_stored_message(state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg_id = data.get("stored_message_id")
    chat_id = data.get("stored_chat_id")

    if msg_id and chat_id:
        await bot.delete_message(chat_id=chat_id, message_id=msg_id)
        await state.update_data(stored_message_id=None, stored_chat_id=None)
