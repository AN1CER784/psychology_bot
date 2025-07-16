from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import as_marked_section, Bold
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.orm_queries.common import orm_get_all_models
from database.orm_queries.user import orm_update_user_status_by_id
from filters.admin_filter import IsAdmin, admin_ids
from kbds.admin_kb import admin_kb, back_admin_kb

admin_router_users_management = Router()
admin_router_users_management.message.filter(IsAdmin())


@admin_router_users_management.callback_query(F.data == "manage_users")
async def manage_users(callback: CallbackQuery, session: AsyncSession):
    """
    Manage users

    :param callback:
    :param session:
    :return:
    """
    await callback.answer()
    all_users = await orm_get_all_models(session, User)
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


@admin_router_users_management.message(lambda message: message.text and message.text.startswith("/block_user"))
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


@admin_router_users_management.message(lambda message: message.text and message.text.startswith("/free_user"))
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
