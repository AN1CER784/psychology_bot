from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.formatting import as_marked_section, Bold
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Test, Topic, ActualActivity
from database.orm_queries.common import orm_get_all_models, orm_delete_model, orm_get_and_update_or_create_model
from filters.admin_filter import IsAdmin
from kbds.admin_kb import admin_user_activities_kb, back_admin_kb

admin_router_activities_management = Router()
admin_router_activities_management.message.filter(IsAdmin())


@admin_router_activities_management.callback_query(F.data == "manage_activities")
async def admin_manage_activity(callback: CallbackQuery):
    """
    Main management menu for activities
    """
    await callback.answer()
    await callback.message.edit_text("Вы можете выбрать одно из следующих действий для управления активностями",
                                     reply_markup=admin_user_activities_kb)


@admin_router_activities_management.callback_query(F.data == "manage_activities")
async def admin_manage_activity(callback: CallbackQuery):
    """
    Main management menu for activities
    """
    await callback.answer()
    await callback.message.edit_text("Вы можете выбрать одно из следующих действий для управления активностями",
                                     reply_markup=admin_user_activities_kb)


@admin_router_activities_management.callback_query(F.data == "del_activity")
async def admin_del_activity(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    message = await generate_activities_message(session, command_line="/del", marker="🗑")
    await send_and_store_message(callback, message_text=message, reply_markup=back_admin_kb, state=state)


@admin_router_activities_management.message(F.text.startswith("/del_test_"))
async def del_test(message: Message, state: FSMContext, session: AsyncSession):
    test_id = int(message.text.split("_")[2])
    await delete_stored_message(state, message.bot)
    await orm_delete_model(session, Test, {"id": test_id})
    await message.answer("Тест удален", reply_markup=admin_user_activities_kb)


@admin_router_activities_management.message(F.text.startswith("/del_topic_"))
async def del_topic(message: Message, state: FSMContext, session: AsyncSession):
    topic_id = int(message.text.split("_")[2])
    await delete_stored_message(state, message.bot)
    try:
        await orm_delete_model(session, Topic, {"id": topic_id})
    except ValueError:
        await message.answer("Рубрика уже удалена или ее не существует", reply_markup=admin_user_activities_kb)
        return
    await message.answer("Рубрика удалена", reply_markup=admin_user_activities_kb)


@admin_router_activities_management.callback_query(F.data == "choose_actual_activity")
async def admin_choose_actual_activity(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.answer()
    message = await generate_activities_message(session, command_line="/activate")
    await send_and_store_message(callback, message_text=message, reply_markup=back_admin_kb, state=state)


@admin_router_activities_management.message(F.text.startswith("/activate_test_"))
async def activate_test(message: Message, state: FSMContext, session: AsyncSession):
    await delete_stored_message(state, message.bot)
    test_id = int(message.text.split("_")[2])
    await orm_get_and_update_or_create_model(session, ActualActivity, {"id": 1, "test_id": test_id})
    await message.answer("Тест стал актуальным для пользователей", reply_markup=admin_user_activities_kb)


@admin_router_activities_management.message(F.text.startswith("/activate_topic_"))
async def activate_topic(message: Message, state: FSMContext, session: AsyncSession):
    await delete_stored_message(state, message.bot)
    topic_id = int(message.text.split("_")[2])

    await orm_get_and_update_or_create_model(session, ActualActivity, {"id": 1, "topic_id": topic_id})
    await message.answer("Рубрика стала актуальной для пользователей", reply_markup=admin_user_activities_kb)


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


async def generate_activities_message(session, command_line, marker="✅"):
    all_tests = await orm_get_all_models(session, Test)
    all_topics = await orm_get_all_models(session, Topic)
    if command_line == "/activate":
        message = "Здесь вы можете выбрать актуальную для пользователей активность\n\n"
    else:
        message = "Здесь вы можете удалить те активности, которые больше не нужны\n\n"

    if all_tests:
        message += as_marked_section(
            Bold("Тесты:\n"),
            *(f"{command_line}_test_{test.id}. Тест - {test.title}\n" for test in all_tests),
            marker=marker,
        ).as_html()
        message += "\n"
    if all_topics:
        message += as_marked_section(
            Bold("Рубрики:\n"),
            *(f"{command_line}_topic_{topic.id}. Рубрика - {topic.title}\n" for topic in all_topics),
            marker=marker,
        ).as_html()
    return message
