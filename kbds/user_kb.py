from datetime import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries.schedule import orm_get_appointment_by_user_id, orm_get_appointments_by_date
from filters.admin_filter import admin_ids


async def get_main_kb(session: AsyncSession, user_id):
    """
    Get main kb depending on who is a user
    :param session:
    :param user_id:
    :return:
    """
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Начать активность 🟢", callback_data="watch_actual_activity"))
    has_appointment = await orm_get_appointment_by_user_id(session, user_id)
    if has_appointment:
        sign_date = datetime.strftime(has_appointment.date_time, "%d.%m-%H:%M")
        builder.add(
            InlineKeyboardButton(text="Просмотреть запись ⏺️", callback_data=f"check_appointment-{sign_date}"))
    else:
        builder.add(InlineKeyboardButton(text="Записаться к специалисту ✍️", callback_data="make_appointment"))
    if user_id in admin_ids:
        builder.add(InlineKeyboardButton(text="Админ панель 🛠", callback_data="admin_panel"))
    builder.adjust(1)
    return builder.as_markup()

back_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="↩️Вернуться", callback_data="back_to_menu")],
])

back_kb_and_cancel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="↩️Вернуться в главное меню", callback_data="back_to_menu")],
    [InlineKeyboardButton(text="Отменить запись ❌", callback_data="cancel_appointment")],
])

share_contact_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Поделиться контактом 📞", request_contact=True, )]
], resize_keyboard=True, one_time_keyboard=True)


def get_callback_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    """
    Generate callback keyboard

    :param btns:
    :param sizes:
    :return:
    """
    keyboard = InlineKeyboardBuilder()
    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))
    return keyboard.adjust(*sizes).as_markup()


async def generate_time_kb_for_user(session: AsyncSession, date: str):
    """
    Generate kb to choose time

    :param session:
    :param date:
    :return:
    """
    kb = InlineKeyboardBuilder()
    data = await orm_get_appointments_by_date(session, date)
    available_times = sorted([datetime.strftime(appointment.date_time, "%H:%M") for appointment in data])
    for time in available_times:
        button_text = f"{time}✅"
        callback = f"getter_time_{time}"
        kb.add(InlineKeyboardButton(text=button_text, callback_data=callback))
    return kb.adjust(1).as_markup()


async def generate_kb_for_topic(current_message: int):
    """
    Generate kb for navigating through topic
    """
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="⬅️Назад",
                                    callback_data=f"topic_message_{current_message - 1}"))
    kb.add(InlineKeyboardButton(text="Далее➡️",
                                callback_data=f"topic_message_{current_message + 1}"))
    return kb.adjust(2).as_markup()


async def generate_kb_for_test(question_index: int):
    """
    Generate kb for any test
    """

    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="⬅️Назад",
                                    callback_data=f"answertest_question_{question_index - 1}_back"))
    kb.add(InlineKeyboardButton(text="Да✅",
                                callback_data=f"answertest_question_{question_index + 1}_yes"))
    kb.add(InlineKeyboardButton(text="Нет❌",
                                callback_data=f"answertest_question_{question_index + 1}_no"))
    return kb.adjust(3).as_markup()
