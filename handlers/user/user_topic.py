from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import  Topic
from handlers.user.user_watch_activity import end_activity, start_activity
from kbds.user_kb import generate_kb_for_topic

user_router_topic = Router()


@user_router_topic.callback_query(F.data == "start_topic")
async def topic_start(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """
    Start topic
    """
    activity_dict = await start_activity(callback, state, session, Topic)
    message = f"Сейчас будет рассмотрен материал на тему {activity_dict['title']}\n\n{activity_dict['description']}"
    await callback.message.edit_text(
        message
    )
    callback_data = "topic_message_0"
    await topic_next(callback, state, session, callback_data)


@user_router_topic.callback_query((F.data.startswith("topic_message_")))
async def topic_next(callback: CallbackQuery, state: FSMContext, session: AsyncSession, callback_data: str | None = None):
    """
    Run topic
    """
    if not callback_data:
        callback_data = callback.data
    await callback.answer()
    data = await state.get_data()
    messages = data.get("activity_items")
    current_message = int(callback_data.split("_")[2])
    if current_message == len(messages) or current_message == -1:
        await callback.message.delete()
        await end_activity(callback, state, session)
    else:
        topic_content = messages[current_message]
        message = f"<b>{topic_content.title}</b>\n\n{topic_content.text}"
        message_data = message, await generate_kb_for_topic(current_message)
        if current_message == 0:
            await callback.message.answer(message_data[0], reply_markup=message_data[1])
        else:
            await callback.message.edit_text(message_data[0], reply_markup=message_data[1])

