from datetime import datetime
from datetime import timedelta

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import User, Schedule, Content, ContentMessage


############# Добавление информации в БД #############

async def orm_add_available_date(session: AsyncSession, data: dict):
    dt_object = datetime.strptime(f'{datetime.now().year} {data["date"]} {data["time"]}', '%Y %m.%d %H:%M')
    obj = Schedule(date_time=dt_object)
    session.add(obj)
    await session.commit()


async def orm_add_user(session: AsyncSession, data: dict):
    user = User(**data)
    session.add(user)
    await session.commit()


async def orm_add_content(session: AsyncSession, titles: list):
    query = select(Content)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Content(title=title["title"]) for title in titles])
    await session.commit()


async def orm_add_content_message(session: AsyncSession, contents: list):
    query = select(ContentMessage)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all(
        [ContentMessage(text=content["message"], content_title=content["content_title"]) for content in contents])
    await session.commit()


############# Обновление информации в БД #############

async def orm_update_appointment_by_user(session: AsyncSession, user_id: int, data: dict):
    date_time = datetime.strptime(f'{datetime.now().year} {data.get('date')} {data.get("time")}', '%Y %m.%d %H:%M')
    query = update(Schedule).where(Schedule.date_time == date_time).values(user_id=user_id)
    await session.execute(query)
    await session.commit()


async def orm_update_user_status_by_id(session: AsyncSession, user_id: int, status: bool):
    query = update(User).where(User.id == user_id).values(status=status)
    await session.execute(query)
    await session.commit()


############# Получение информации из БД #############

async def orm_get_available_dates(session: AsyncSession):
    query = select(Schedule).where(Schedule.user_id is None)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_appointment_by_user_id(session: AsyncSession, user_id: int):
    query = select(Schedule).where(Schedule.user_id == user_id).options(selectinload(Schedule.user))
    result = await session.execute(query)
    return result.scalar()


async def orm_get_appointment_by_date_time(session: AsyncSession, date: str, time: str):
    dt_object = datetime.strptime(f'{datetime.now().year} {date} {time}', '%Y %m.%d %H:%M')
    query = select(Schedule).where(Schedule.date_time == dt_object).options(selectinload(Schedule.user))
    result = await session.execute(query)
    return result.scalar()


async def orm_get_all_schedule(session: AsyncSession):
    query = select(Schedule).options(selectinload(Schedule.user))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_appointments_by_date(session: AsyncSession, date: str):
    dt_object = datetime.strptime(f'{datetime.now().year} {date}', '%Y %m.%d')
    next_day = dt_object + timedelta(days=1)
    query = select(Schedule).where(Schedule.date_time >= dt_object, Schedule.date_time < next_day).options(selectinload(Schedule.user))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_user_by_id(session: AsyncSession, user_id: int):
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_all_users(session: AsyncSession):
    query = select(User)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_content_message_by_title_and_id(session: AsyncSession, title: str, message_id: int):
    query = select(ContentMessage).where(ContentMessage.content_title == title, ContentMessage.id == message_id)
    result = await session.execute(query)
    return result.scalars().first()


async def orm_get_amount_of_messages_by_title(session: AsyncSession, title: str):
    query = select(ContentMessage).where(ContentMessage.content_title == title)
    result = await session.execute(query)
    return len(result.scalars().all())


async def orm_get_first_message_by_title(session: AsyncSession, title: str):
    query = select(ContentMessage).where(ContentMessage.content_title == title).order_by(ContentMessage.id.asc())
    result = await session.execute(query)
    return result.scalars().first()


async def orm_get_ending_of_test(session: AsyncSession, test_num: int):
    query = select(ContentMessage).where(ContentMessage.content_title == f"test_{test_num}")
    result = await session.execute(query)
    if test_num == 1:
        return result.scalars().all()[-3:]
    elif test_num == 2:
        return result.scalars().all()[-4:]


############# Удаление информации из БД #############

async def orm_del_available_date(session: AsyncSession, data: dict):
    dt_object = datetime.strptime(f'{datetime.now().year} {data["date"]} {data["time"]}', '%Y %m.%d %H:%M')
    query = delete(Schedule).where(Schedule.date_time == dt_object)
    await session.execute(query)
    await session.commit()


async def orm_del_user_appointment(session: AsyncSession, user_id: int):
    query = delete(Schedule).where(Schedule.user_id == user_id)
    await session.execute(query)
    await session.commit()


async def orm_del_outdate_appointments(session: AsyncSession):
    query = delete(Schedule).where(Schedule.date_time < datetime.now())
    await session.execute(query)
    await session.commit()
