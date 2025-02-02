
from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import as_marked_section, Bold
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_appointment_by_date_time, orm_get_appointments_by_date, orm_del_available_date, \
    orm_add_available_date, orm_get_all_schedule, orm_get_all_users, orm_update_user_status_by_id
from filters.admin_filter import IsAdmin, admin_ids
from kbds.admin_kb import admin_kb, generate_time_kb_for_admin, back_admin_kb, generate_back_kb_to_time_admin
from kbds.schedule_kb import generate_schedule_kb

admin_router = Router()
admin_router.message.filter(IsAdmin())


@admin_router.callback_query(F.data == "admin_panel")
async def admin(callback: CallbackQuery):
    """
    Open admin panel

    :param callback:
    :return:
    """
    await callback.answer()
    await callback.message.edit_text("Вы вошли в админ панель", reply_markup=admin_kb)


@admin_router.callback_query(F.data == "schedule")
async def admin_day_choice(callback: CallbackQuery, session: AsyncSession):
    """
    Choose day for consultation

    :param callback:
    :param session:
    :return:
    """
    await callback.answer()
    await callback.message.edit_text("Вы можете составить график на следующую неделю\nВыберите день недели",
                                     reply_markup=await generate_schedule_kb(session, "set"))


@admin_router.callback_query(F.data.startswith('set_'))
async def admin_time_choice(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """
    Choose time for consultation

    :param callback:
    :param state:
    :param session:
    :return:
    """
    await callback.answer()
    date = callback.data.split('_')[1]
    await callback.message.edit_text("Выберите время", reply_markup=await generate_time_kb_for_admin(session, date))
    await state.update_data(date=date)


@admin_router.callback_query(F.data.startswith('setter_time_'))
async def admin_set_choice(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """
    Set time for consultation

    :param callback:
    :param state:
    :param session:
    :return:
    """
    await callback.answer()
    await state.update_data(time=callback.data.split('_')[2])
    await admin_edit_time_in_database(callback, state, session)


@admin_router.callback_query(F.data == "submit")
async def admin_submit_choice(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """
    Submit changes

    :param callback:
    :param state:
    :param session:
    :return:
    """
    await callback.answer()
    data = await state.get_data()
    date = data.get('date')
    time_data = await orm_get_appointments_by_date(session, date)
    if time_data:
        message_text = f"Запись на консультацию доступна\n<b>{date}</b>\n"
        for appointment in time_data:
            time = datetime.strftime(appointment.date_time, "%H:%M")
            message_text += f"<b>{time}</b>, "
        await callback.message.edit_text(message_text.strip(", "), reply_markup=admin_kb)
    else:
        await callback.message.edit_text("Запись на консультацию в этот день недоступна", reply_markup=admin_kb)
    await state.clear()


async def admin_edit_time_in_database(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """
    Edit time in database

    :param callback:
    :param state:
    :param session:
    :return:
    """
    await callback.answer()
    data = await state.get_data()
    if callback.data.split('_')[-1] == 'close':
        await orm_add_available_date(session, data)
    elif callback.data.split('_')[-1] == 'open':
        await orm_del_available_date(session, data)
    await callback.message.edit_reply_markup(reply_markup=await generate_time_kb_for_admin(session, data.get('date')))


@admin_router.callback_query(F.data == "watch_schedule")
async def watch_schedule(callback: CallbackQuery, session: AsyncSession):
    """
    Watch all schedule

    :param callback:
    :param session:
    :return:
    """
    await callback.answer()
    dates_data = await orm_get_all_schedule(session)
    schedule_dict = {"available_schedule": [], "users_schedule": []}
    message_text = ""
    if dates_data:
        for appointment in dates_data:
            if appointment.user_id is None:
                schedule_dict["available_schedule"].append(appointment)
            else:
                schedule_dict["users_schedule"].append(appointment)
    if schedule_dict["available_schedule"]:
        message_text += as_marked_section(
            Bold("Доступное расписание:"),
            *(f"{datetime.strftime(appointment.date_time, "%m.%d")} в {datetime.strftime(appointment.date_time, "%H:%M")}" for appointment in schedule_dict["available_schedule"]),
            marker="✅",
        ).as_html()
    if schedule_dict["users_schedule"]:
        message_text += as_marked_section(
            Bold("\n\nЗаписи на консультацию:"),
            *(f"@{appointment.user.name} - {appointment.user.phone}, {datetime.strftime(appointment.date_time, "%m.%d")} в {datetime.strftime(appointment.date_time, "%H:%M")}" for appointment in schedule_dict["users_schedule"]),
            marker="⏺️",
        ).as_html()
    if not schedule_dict.values():
        message_text += "Расписание на неделю не составлено"

    await callback.message.edit_text(message_text, reply_markup=back_admin_kb)


@admin_router.callback_query(F.data.startswith("watch_user_appointment_"))
async def watch_user_appointment(callback: CallbackQuery, session: AsyncSession):
    """
    Watch user appointment info

    :param callback:
    :param session:
    :return:
    """
    await callback.answer()
    time, date = callback.data.split('_')[-1], callback.data.split('_')[-2]
    user_data = await orm_get_appointment_by_date_time(session, date, time)
    await callback.message.edit_text(
        f"Пользователь - @{user_data.user.name}\nТелефон - +{user_data.user.phone}\nДата записи - {date}\nВремя записи - {time}",
        reply_markup=await generate_back_kb_to_time_admin(date))


@admin_router.callback_query(F.data == "manage_users")
async def manage_users(callback: CallbackQuery, session: AsyncSession):
    """
    Manage users

    :param callback:
    :param session:
    :return:
    """
    await callback.answer()
    all_users = await orm_get_all_users(session)
    free_users = []
    blocked_users = []
    for user in all_users:
        if user.status:
            free_users.append(user)
        else:
            blocked_users.append(user)
    message_text = "Добро пожаловать в управление пользователями бота.\nДля блокировки пользователя найдите соответствующего пользователя и нажмите на соответсвующую команду:\nblock_user - заблокировать\nfree_user - разблокировать\n\n"
    if free_users:
        message_text += as_marked_section(
            Bold("Активные пользователи:"),
            *(f"/block_user_{user.id} - @{user.name} - +{user.phone}" for user in free_users),
            marker="✅",
        ).as_html()
    else:
        message_text += as_marked_section(
            Bold("Активные пользователи:"),
            "Нет активных пользователей",
            marker="✅",
        ).as_html()

    if blocked_users:
        message_text += as_marked_section(
            Bold("\n\nЗаблокированные пользователи:"),
            *(f"/free_user_{user.id} - @{user.name} - +{user.phone}" for user in blocked_users),
            marker="🚫",
        ).as_html()
    else:
        message_text += as_marked_section(
            Bold("\n\nЗаблокированные пользователи:"),
            "Нет заблокированных пользователей",
            marker="🚫",
        ).as_html()

    await callback.message.edit_text(message_text, reply_markup=back_admin_kb)


@admin_router.message(lambda message: message.text and message.text.startswith("/block_user"))
async def block_user(message: Message, session: AsyncSession):
    """
    Block user

    :param message:
    :param session:
    :return:
    """
    user_id = int(message.text.split('_')[-1])
    if user_id not in admin_ids:
        await orm_update_user_status_by_id(session, user_id, False)
        await message.answer("Пользователь заблокирован", reply_markup=admin_kb)
    else:
        await message.answer("Нельзя заблокировать администратора", reply_markup=admin_kb)


@admin_router.message(lambda message: message.text and message.text.startswith("/free_user"))
async def free_user(message: Message, session: AsyncSession):
    """
    Free user

    :param message:
    :param session:
    :return:
    """
    user_id = int(message.text.split('_')[-1])
    await orm_update_user_status_by_id(session, user_id, True)
    await message.answer("Пользователь разблокирован", reply_markup=admin_kb)
