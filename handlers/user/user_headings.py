from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_content_message_by_title_and_id, orm_get_amount_of_messages_by_title, \
    orm_get_first_message_by_title
from kbds.user_kb import generate_kb_for_chapters, generate_after_chapter_kb

user_chapters = Router()


@user_chapters.callback_query(F.data.startswith("heading"))
async def chapters_processing(callback: CallbackQuery, session: AsyncSession):
    """
    Processing of all chapters

    :param session:
    :param callback:
    :return:
    """
    await callback.answer()
    processed_data = callback.data.split("_")
    current_heading = int(processed_data[-3])
    current_chapter = int(processed_data[-2])
    current_message = int(processed_data[-1])
    title = f"chapter_{current_heading}_{current_chapter}"
    messages_amount = await orm_get_amount_of_messages_by_title(session, title)
    first_message = await orm_get_first_message_by_title(session, title)
    message = await orm_get_content_message_by_title_and_id(session, title, current_message + first_message.id - 1)
    if current_message != messages_amount + 1:
        await callback.message.edit_text(message.text,
                                         reply_markup=await generate_kb_for_chapters(current_heading, current_chapter,
                                                                                     current_message))
    else:
        await callback.message.delete_reply_markup()
        await callback.message.answer("Если вы столкнулись с трудностями в знакомстве и построении отношений,"
                                      " обратитесь к профессиональному семейному психологу",
                                      reply_markup=await generate_after_chapter_kb(current_heading))
