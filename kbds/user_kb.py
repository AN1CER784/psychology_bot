from datetime import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_appointments_by_date, orm_get_appointment_by_user_id
from filters.admin_filter import admin_ids


async def get_headings_kb(session: AsyncSession, user_id):
    """
    Get main headings kb depending on who is a user
    :param session:
    :param user_id:
    :return:
    """
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Трудности в построении отношений 🧐", callback_data="heading_1"))
    builder.add(InlineKeyboardButton(text="Как найти спутника жизни? 💕", callback_data="heading_2"))
    builder.add(InlineKeyboardButton(text="Сепарация ✂️", callback_data="heading_3"))
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


first_heading_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Ошибки при построении отношений 🚫", callback_data="heading_1_1_1")],
    [InlineKeyboardButton(text="Как вести разговор об отношениях? 👩‍❤️‍👨", callback_data="heading_1_2_1")],
    [InlineKeyboardButton(text="Тест: Умеете ли вы мириться? 🤝", callback_data="test_1")],
    [InlineKeyboardButton(text="⬅️Назад", callback_data="back_to_headings")],
])

second_heading_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Советы 💁", callback_data="heading_2_1_1")],
    [InlineKeyboardButton(text="Откровенные разговоры с партнером 🙊", callback_data="heading_2_2_1")],
    [InlineKeyboardButton(text="⬅️Назад", callback_data="back_to_headings")],
])

third_heading_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Тест: Уровень сепарации 🧩", callback_data="test_2")],
    [InlineKeyboardButton(text="⬅️Назад", callback_data="back_to_headings")]
])

back_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="↩️Вернуться в главное меню", callback_data="back_to_headings")],
])

back_kb_and_cancel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="↩️Вернуться в главное меню", callback_data="back_to_headings")],
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


async def generate_after_chapter_kb(heading: int):
    """
    Generate kb after completing chapter

    :param heading:
    :return:
    """
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Записаться к специалисту ✍️", callback_data="make_appointment"))
    kb.add(InlineKeyboardButton(text="↩️Вернуться к выбору раздела",
                                callback_data=f"back_to_chapters_{heading}"))
    return kb.adjust(1).as_markup()


async def generate_kb_for_chapters(heading: int, current_chapter: int, current_message: int):
    """
    Generate kb for navigating through chapters

    :param heading:
    :param current_chapter:
    :param current_message:
    :return:
    """
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="⬅️Назад",
                                callback_data=f"back_to_chapters_{heading}"
                                if current_message == 1
                                else f"heading_{heading}_{current_chapter}_{current_message - 1}"))
    kb.add(InlineKeyboardButton(text="Далее➡️",
                                callback_data=f"heading_{heading}_{current_chapter}_{current_message + 1}"))
    return kb.adjust(2).as_markup()


async def generate_kb_for_test(test_num: int, question_index: int, current_score: int):
    """
    Generate kb for any test

    :param test_num:
    :param question_index:
    :param current_score:
    :return:
    """

    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Верно✅",
                                callback_data=f"answertest_{test_num}_question_{question_index + 1}-{current_score + 1}"))
    kb.add(InlineKeyboardButton(text="Неверно❌",
                                callback_data=f"answertest_{test_num}_question_{question_index + 1}-{current_score}"))
    if test_num == 1:
        kb.add(InlineKeyboardButton(text="↩️Назад", callback_data="back_to_chapters_from_test1"))
    elif test_num == 2:
        kb.add(InlineKeyboardButton(text="↩️Назад", callback_data="back_to_chapters_from_test2"))
    return kb.adjust(2).as_markup()
