from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries.activities import orm_get_actual_activity, orm_get_activity_items_by_id
from kbds.user_kb import get_main_kb, back_kb, get_callback_btns

user_router_activity = Router()


@user_router_activity.callback_query(F.data == "watch_actual_activity")
async def watch_activity(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    actual_activity = await orm_get_actual_activity(session)
    if actual_activity is None:
        await callback.message.edit_text("Активность еще не была добавлена\nДождитесь ее добавления администратором",
                                         reply_markup=back_kb)
    else:
        if actual_activity["type"] == "topic":
            await callback.message.edit_text("Вы можете начать рубрику", reply_markup=get_callback_btns(
                btns={"Начать": "start_topic", "↩️Вернуться": "back_to_menu"}))
        else:
            await callback.message.edit_text("Вы можете начать тест",
                                             reply_markup=get_callback_btns(
                                                 btns={"Начать": "start_test", "↩️Вернуться": "back_to_menu"}))

        await state.update_data(activity=actual_activity["object"])


async def end_activity(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """
    End activity
    """
    await callback.answer()
    await state.clear()
    await callback.message.answer("Вы можете обратиться к специалисту по кнопке ниже либо начать активность заново",
                                  reply_markup=await get_main_kb(session, callback.message.from_user.id))


async def start_activity(callback: CallbackQuery, state: FSMContext, session: AsyncSession, model):
    """
    Start activity
    """
    await callback.answer()
    data = await state.get_data()
    activity = data.get("activity")
    title = activity.title
    description = activity.description
    activity_items = await orm_get_activity_items_by_id(session, model, activity.id)
    activity_items_list = [item for item in activity_items]
    await state.update_data(activity_items=activity_items_list)
    return {"title": title, "description": description}
