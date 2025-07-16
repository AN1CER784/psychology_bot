from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from common.states import Activities, TestFlow
from common.utils import get_dict_from_data
from database.models import Test, TestItem
from database.orm_queries.activities import orm_get_activity_by_title
from database.orm_queries.common import orm_add_model
from filters.admin_filter import IsAdmin
from kbds.admin_kb import back_admin_kb, admin_add_test_item_kb, admin_user_activities_kb, admin_continue_kb, \
    admin_start_fill_test_kb
admin_router_test = Router()
admin_router_test.message.filter(IsAdmin())


@admin_router_test.message(StateFilter(Activities.test_name))
async def admin_fill_test(message: Message, state: FSMContext):
    await state.update_data(activity_title=message.text)
    await message.answer("Введите описание теста", reply_markup=back_admin_kb)
    await state.set_state(Activities.test_description)


@admin_router_test.message(StateFilter(Activities.test_description))
async def admin_fill_test_description(message: Message, state: FSMContext):
    data = await get_dict_from_data(state, message, name_string="activity_title")
    await state.update_data(default_data={"title": data["title"], "description": data["description"]})
    await message.answer("Введите сообщение при успешном прохождении теста", reply_markup=back_admin_kb)
    await state.set_state(Activities.test_high_score_message)


@admin_router_test.message(StateFilter(Activities.test_high_score_message))
async def admin_fill_test_high_score(message: Message, state: FSMContext):
    await state.update_data(high_score_message=message.text)
    await state.set_state(Activities.test_medium_score_message)
    await message.answer("Введите сообщение при среднем прохождении теста", reply_markup=back_admin_kb)


@admin_router_test.message(StateFilter(Activities.test_medium_score_message))
async def admin_fill_test_medium_score(message: Message, state: FSMContext):
    await state.update_data(medium_score_message=message.text)
    await state.set_state(Activities.test_low_score_message)
    await message.answer("Введите сообщение при плохом прохождении теста", reply_markup=back_admin_kb)


@admin_router_test.message(StateFilter(Activities.test_low_score_message))
async def admin_fill_test_low_score(message: Message, state: FSMContext, session: AsyncSession):
    low_score_message = message.text
    data = await state.get_data()
    orm_data = data.get("default_data") | {"high_score_message": data.get("high_score_message"),
                                           "medium_score_message": data.get("medium_score_message"),
                                           "low_score_message": low_score_message}
    await orm_add_model(session, Test, orm_data)
    await state.set_state(TestFlow.choosing_test)
    await message.answer("Тест добавлен, заполните его контентом", reply_markup=admin_start_fill_test_kb)


@admin_router_test.message(StateFilter(TestFlow.choosing_test), F.data == "add_question")
async def admin_fill_topic_content(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(f"Введите вопрос теста")
    await state.set_state(TestFlow.input_question)


@admin_router_test.message(StateFilter(TestFlow.input_question))
async def input_topic_item_content(message: Message, state: FSMContext, session: AsyncSession):
    question = message.text
    data = await state.get_data()
    test = await orm_get_activity_by_title(session, data.get("activity_title"), Test)
    await orm_add_model(session, TestItem,
                        {"question": question, "test_id": test.id})
    await message.answer(
        "Вопрос для теста добавлен! Хотите добавить ещё один?",
        reply_markup=admin_add_test_item_kb
    )
    await state.set_state(TestFlow.choosing_test)


@admin_router_test.callback_query(F.data == "finish_test")
async def finish_topic(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("Тест успешно добавлен", reply_markup=admin_user_activities_kb)
    await state.clear()
