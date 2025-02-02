from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_appointments_by_date

back_admin_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️Назад", callback_data="back_to_admin")],
])

admin_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Добавить/Удалить консультацию🗓", callback_data="schedule")],
    [InlineKeyboardButton(text="Просмотреть расписание 📝", callback_data="watch_schedule")],
    [InlineKeyboardButton(text="Управление пользователями ⚖️", callback_data="manage_users")],
    [InlineKeyboardButton(text="Выйти из админ панели ↩️", callback_data="back_to_headings")]
])

block_users_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Заблокировать пользователя ❌", callback_data="block_user"),
     InlineKeyboardButton(text="Разблокировать пользователя ✅", callback_data="unblock_user")],
    [InlineKeyboardButton(text="⬅️Назад", callback_data="back_to_admin")]
])


async def generate_back_kb_to_time_admin(date: str):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="⬅️Назад", callback_data=f"set_{date}"))
    return kb.adjust(1).as_markup()


async def generate_time_kb_for_admin(session: AsyncSession, date: str):
    kb = InlineKeyboardBuilder()
    times = (
        "10:00", "10:30", "11:00", "11:30", "12:00", "12:30",
        "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
        "16:00", "16:30", "17:00", "17:30", "18:00", "18:30",
        "19:00", "19:30", "20:00", "20:30", "21:00", "21:30"
    )
    registered_times = []
    opened_times = []
    res = await orm_get_appointments_by_date(session, date)
    for appointment in res:
        if appointment.user_id is not None:
            registered_times.append(appointment.date_time.strftime("%H:%M"))
        else:
            opened_times.append(appointment.date_time.strftime("%H:%M"))
    for time in times:
        if time in registered_times:
            button_text = f"{time}📝"
            callback = f"watch_user_appointment_{date}_{time}"
        elif time in opened_times:
            button_text = f"{time}✅"
            callback = f"setter_time_{time}_open"
        else:
            button_text = f"{time}❌"
            callback = f"setter_time_{time}_close"
        kb.add(InlineKeyboardButton(text=button_text, callback_data=callback))
    kb.add(InlineKeyboardButton(text="Подтвердить✅", callback_data="submit"))
    return kb.adjust(4).as_markup()
