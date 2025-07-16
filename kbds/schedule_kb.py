from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from common.utils import generate_dates
from database.orm_queries.schedule import orm_get_appointments_by_date


async def generate_schedule_kb(session: AsyncSession, side: str):
    """
    Generate schedule kb for admins and users

    :param session:
    :param side:
    :return:
    """
    kb = InlineKeyboardBuilder()
    dates = await generate_dates()
    for date in dates:
        callback = f"{side}_{date}"
        button_text = f"{date}"
        date_data = await orm_get_appointments_by_date(session, date)
        if side == "set":
            if any(appointment.user_id is not None for appointment in date_data):
                button_text += "👤"

        if date_data and any(appointment.user_id is None for appointment in date_data):
            button_text += "✅"
            callback += "_open"
        else:
            button_text += "❌"
            callback += "_close"

        kb.add(InlineKeyboardButton(text=button_text,
                                    callback_data=callback))
    if side == "get":
        kb.add(InlineKeyboardButton(text="⬅️Назад", callback_data="back_to_headings"))
    return kb.adjust(1).as_markup()
