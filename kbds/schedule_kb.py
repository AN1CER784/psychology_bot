from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from common.dates_generator import generate_dates
from database.orm_query import orm_get_appointments_by_date


async def generate_schedule_kb(session: AsyncSession, side: str):
    kb = InlineKeyboardBuilder()
    dates = await generate_dates()
    for date in dates:
        callback = f"{side}_{date}"
        button_text = f"{date}"
        if side == "get":
            date_data = await orm_get_appointments_by_date(session, date)
            if date_data:
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
