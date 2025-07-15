from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from kbds.admin_kb import admin_kb
from kbds.user_kb import second_heading_kb, first_heading_kb, get_headings_kb, third_heading_kb

user_router_back = Router()
admin_router_back = Router()


@user_router_back.callback_query(F.data == "back_to_headings")
async def back_to_headings(callback: CallbackQuery, session: AsyncSession):
    """
    Back to headings

    :param callback:
    :return:
    """
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("Вы в главном меню🙂\n\n"
                                  "Можете выбрать любую рубрику или же сразу записаться на консультацию",
                                  reply_markup=await get_headings_kb(session, callback.from_user.id))


@user_router_back.callback_query(F.data == "back_to_chapters_1")
async def back_to_heading1(callback: CallbackQuery, state: FSMContext):
    """
    Back to heading 1

    :param state:
    :param callback:
    :return:
    """
    await callback.answer()
    await callback.message.edit_text("Можете выбрать то, что вас интересует по материалам рубрики\n"
                                     "<b>Трудности в построении отношений</b>", reply_markup=first_heading_kb)


@user_router_back.callback_query(F.data == "back_to_chapters_2")
async def back_to_heading2(callback: CallbackQuery, state: FSMContext):
    """
    Back to heading 2

    :param callback:
    :param state:
    :return:
    """
    await callback.answer()
    data = await state.get_data()
    initial_message_id = data.get('initial_message_id')
    chat_id = data.get('chat_id')
    await callback.message.edit_text("Можете выбрать то, что вас интересует по материалам рубрики\n"
                                     "<b>Как найти спутника жизни?</b>", reply_markup=second_heading_kb)
    if initial_message_id:
        await callback.bot.delete_message(chat_id=chat_id, message_id=initial_message_id)
    await state.clear()


@user_router_back.callback_query(F.data == "back_to_chapters_3")
async def back_to_heading3(callback: CallbackQuery, state: FSMContext):
    """
    Back to heading 3

    :param state:
    :param callback:
    :return:
    """
    await callback.answer()
    await callback.message.edit_text("Можете выбрать то, что вас интересует по материалам рубрики\n"
                                     "<b>Сепарация</b> ✂️", reply_markup=third_heading_kb)


@user_router_back.callback_query(F.data.startswith("back_to_chapters_from_test"))
async def back_to_chapters_from_test(callback: CallbackQuery, state: FSMContext):
    """
    Back to chapters from test

    :param state:
    :param callback:
    :return:
    """
    data = await state.get_data()
    init_message_id, init_message_chat_id = data.get('init_message_id'), data.get('init_message_chat_id')
    await callback.message.delete()
    await callback.bot.delete_message(chat_id=init_message_chat_id, message_id=init_message_id)
    await callback.answer()
    if 'test1' in callback.data:
        await callback.message.answer("Можете выбрать то, что вас интересует по материалам рубрики\n"
                                         "<b>Трудности в построении отношений</b>", reply_markup=first_heading_kb)
    else:
        await callback.message.answer("Можете выбрать то, что вас интересует по материалам рубрики\n"
                                         "<b>Как найти спутника жизни?</b>", reply_markup=third_heading_kb)


@admin_router_back.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery):
    """
    Go back to main admin panel
    :param callback:
    :return:
    """
    await callback.answer()
    await callback.message.edit_text("Вы в панели админа", reply_markup=admin_kb)
