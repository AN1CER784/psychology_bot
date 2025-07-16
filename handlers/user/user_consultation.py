import os
from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from config import bot
from database.orm_queries.common import orm_add_model
from database.orm_queries.schedule import orm_get_all_schedule, orm_get_appointment_by_user_id, \
    orm_del_user_appointment, orm_update_appointment_by_user
from database.orm_queries.user import orm_get_user_by_id
from kbds.schedule_kb import generate_schedule_kb
from kbds.user_kb import share_contact_kb, generate_time_kb_for_user, back_kb_and_cancel, back_kb

user_router_consult = Router()


@user_router_consult.callback_query(F.data == "make_appointment")
async def user_day_choice(callback: CallbackQuery, session: AsyncSession):
    """
    Choose a day for consultation or send a note about the impossibility of this

    :param session:
    :param callback:
    :return:
    """
    await callback.answer()
    await callback.message.delete()
    data = await orm_get_all_schedule(session)
    if data:
        await callback.message.answer(
            "Открыта запись на следующую неделю\nВыберите день недели",
            reply_markup=await generate_schedule_kb(session, "get"))
    else:
        await callback.message.answer(
            "На данный момент запись не доступна\nМожете связаться напрямую по ссылке:\nhttps://t.me/natalya1970131")


@user_router_consult.callback_query(F.data.startswith('get_'), F.data.endswith('_open'))
async def user_time_choice(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """
    Go to choose time for consultation

    :param callback:
    :param state:
    :param session:
    :return:
    """
    await callback.answer()
    date = callback.data.split('_')[1]
    await callback.message.edit_text("Выберите время", reply_markup=await generate_time_kb_for_user(session, date))
    await state.update_data(date=date)


@user_router_consult.callback_query(F.data.startswith('get_'), F.data.endswith('_close'))
async def closed_user_day_choice(callback: CallbackQuery, session: AsyncSession):
    """
    This day for consultation is closed

    :param callback:
    :param session:
    :return:
    """
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("Запись на консультацию в этот день недоступна ❌",
                                  reply_markup=await generate_schedule_kb(session, "get"))


@user_router_consult.callback_query(F.data.startswith("check_appointment"))
async def check_appointment(callback: CallbackQuery):
    """
    Check the appointment

    :param callback:
    :return:
    """
    await callback.answer()
    sign_date = callback.data.split('-')[1]
    sign_time = callback.data.split('-')[2]
    await callback.message.edit_text(
        f"Вы записаны на консультацию\nДата записи - {sign_date}\nВремя записи - {sign_time}",
        reply_markup=back_kb_and_cancel)


@user_router_consult.callback_query(F.data == "cancel_appointment")
async def cancel_appointment(callback: CallbackQuery, session: AsyncSession):
    """
    Cancel the appointment

    :param callback:
    :param session:
    :return:
    """
    await callback.answer()
    data = await orm_get_appointment_by_user_id(session, callback.from_user.id)
    await orm_del_user_appointment(session, callback.from_user.id)
    await callback.message.edit_text("Запись на консультацию отменена ❌", reply_markup=back_kb)
    await bot.send_message(os.getenv("GROUP_ID"),
                           text=f"Запись на консультацию отменена ❌\n"
                                f'<b>@{data.user.name} - +{data.user.phone}\n{datetime.strftime(data.date_time, "%d.%m")} - {datetime.strftime(data.date_time, "%H:%M")}</b>')


@user_router_consult.message(F.contact.phone_number)
async def make_appointment(message: Message, state: FSMContext, session: AsyncSession):
    """
    Make an appointment and save it to database

    :param message:
    :param state:
    :param session:
    :return:
    """
    data = await state.get_data()
    if not await orm_get_user_by_id(session, message.from_user.id):
        user_data = {'id': message.from_user.id, 'name': message.from_user.username,
                     'phone': message.contact.phone_number.strip('+'), 'status': True}
        await orm_add_model(session, "User", user_data)
    await orm_update_appointment_by_user(session, message.from_user.id, data)
    await message.answer(f"Запись на консультацию оформлена\n"
                         f"<b>{data.get('date')} - {data.get('time')}</b> ✅\nОжидайте, с вами свяжется специалист",
                         reply_markup=back_kb)
    await bot.send_message(os.getenv("GROUP_ID"),
                           text=f"Новая запись на консультацию\n"
                                f"<b>{data.get('date')} - {data.get('time')}</b> ✅")
    await message.forward(chat_id=os.getenv("GROUP_ID"))
    await state.clear()


@user_router_consult.callback_query(F.data.startswith('getter_time_'))
async def user_contacts_share(callback: CallbackQuery, state: FSMContext):
    """
    Share contacts with us

    :param callback:
    :param state:
    :return:
    """
    await callback.answer()
    time = callback.data.split('_')[2]
    await state.update_data(time=time)
    await callback.message.delete()
    await callback.message.answer("Поделитесь своими контактными данными для записи на консультацию",
                                  reply_markup=share_contact_kb)
