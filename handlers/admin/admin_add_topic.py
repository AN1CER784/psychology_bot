from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from common.states import TopicFlow, Activities
from common.utils import get_dict_from_data
from database.models import Topic, TopicItem
from database.orm_queries.activities import orm_get_activity_by_title
from database.orm_queries.common import orm_add_model
from filters.admin_filter import IsAdmin
from kbds.admin_kb import back_admin_kb, admin_add_topic_item_kb, admin_user_activities_kb, admin_start_fill_topic_kb

admin_router_topic = Router()
admin_router_topic.message.filter(IsAdmin())


@admin_router_topic.callback_query(F.data == "add_topic_activity")
async def admin_choice_topic(callback: CallbackQuery, state: FSMContext):
    """
    Choice of topic by admin
    """
    await callback.answer()
    await callback.message.edit_text("Введите название рубрики", reply_markup=back_admin_kb)
    await state.set_state(Activities.topic_name)


@admin_router_topic.callback_query(F.data == "add_test_activity")
async def admin_choice_topic(callback: CallbackQuery, state: FSMContext):
    """
    Choice of test by admin
    """
    await callback.answer()
    await callback.message.edit_text("Введите название теста", reply_markup=back_admin_kb)
    await state.set_state(Activities.test_name)


@admin_router_topic.message(StateFilter(Activities.topic_name))
async def admin_fill_topic(message: Message, state: FSMContext):
    """
    Fill topic by admin
    """
    await state.update_data(activity_title=message.text)
    await message.answer("Введите описание рубрики", reply_markup=back_admin_kb)
    await state.set_state(Activities.topic_description)


@admin_router_topic.message(StateFilter(Activities.topic_description))
async def admin_fill_topic_description(message: Message, state: FSMContext, session: AsyncSession):
    data = await get_dict_from_data(state, message, "activity_title")
    await orm_add_model(session, Topic, {"title": data["title"], "description": data["description"]})
    await message.answer(f"Рубрика {data['title']} успешно добавлена\nЗаполните ее контентом",
                         reply_markup=admin_start_fill_topic_kb)
    await state.set_state(TopicFlow.choosing_topic)


@admin_router_topic.callback_query((StateFilter(TopicFlow.choosing_topic)), (F.data == "add_topic_item"))
async def admin_fill_topic_content(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(f"Введите заголовок раздела рубрики", )
    await state.set_state(TopicFlow.input_title)


@admin_router_topic.message(StateFilter(TopicFlow.input_title))
async def input_topic_item_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Теперь введите содержание раздела")
    await state.set_state(TopicFlow.input_content)


@admin_router_topic.message(StateFilter(TopicFlow.input_content))
async def input_topic_item_content(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    topic = await orm_get_activity_by_title(session, data.get("activity_title"), Topic)
    await orm_add_model(session, TopicItem,
                        {"title": data.get("title"), "text": message.text, "topic_id": topic.id})
    await message.answer(
        "Раздел добавлен! Хотите добавить ещё один?  Тогда введите его и отправьте",
        reply_markup=admin_add_topic_item_kb
    )
    await state.set_state(TopicFlow.choosing_topic)


@admin_router_topic.callback_query(F.data == "finish_topic")
async def finish_topic(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("Рубрика успешно добавлена", reply_markup=admin_user_activities_kb)
    await state.clear()
