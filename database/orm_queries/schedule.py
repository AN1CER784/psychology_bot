from datetime import datetime
from datetime import timedelta

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Schedule

"""ORM QUERIES TO INSERT DATA"""


async def orm_update_appointment_by_user(session: AsyncSession, user_id: int, data: dict):
    date_time = datetime.strptime(f'{datetime.now().year} {data.get("date")} {data.get("time")}', '%Y %d.%m %H:%M')
    query = update(Schedule).where(Schedule.date_time == date_time).values(user_id=user_id)
    await session.execute(query)
    await session.commit()


async def orm_add_available_date(session: AsyncSession, data: dict):
    dt_object = datetime.strptime(f'{datetime.now().year} {data["date"]} {data["time"]}', '%Y %d.%m %H:%M')
    obj = Schedule(date_time=dt_object)
    session.add(obj)
    await session.commit()


"""ORM QUERIES TO RETRIEVE DATA"""


async def orm_get_available_dates(session: AsyncSession):
    query = select(Schedule).where(Schedule.user_id is None)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_appointment_by_user_id(session: AsyncSession, user_id: int):
    query = select(Schedule).where(Schedule.user_id == user_id).options(selectinload(Schedule.user))
    result = await session.execute(query)
    return result.scalar()


async def orm_get_appointment_by_date_time(session: AsyncSession, date: str, time: str):
    dt_object = datetime.strptime(f'{datetime.now().year} {date} {time}', '%Y %d.%m %H:%M')
    query = select(Schedule).where(Schedule.date_time == dt_object).options(selectinload(Schedule.user))
    result = await session.execute(query)
    return result.scalar()


async def orm_get_all_schedule(session: AsyncSession):
    query = select(Schedule).options(selectinload(Schedule.user))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_appointments_by_date(session: AsyncSession, date: str):
    dt_object = datetime.strptime(f'{datetime.now().year} {date}', '%Y %d.%m')
    next_day = dt_object + timedelta(days=1)
    query = select(Schedule).where(Schedule.date_time >= dt_object, Schedule.date_time < next_day).options(
        selectinload(Schedule.user))
    result = await session.execute(query)
    return result.scalars().all()


"""ORM QUERIES TO DELETE DATA"""


async def orm_del_available_date(session: AsyncSession, data: dict):
    dt_object = datetime.strptime(f'{datetime.now().year} {data["date"]} {data["time"]}', '%Y %d.%m %H:%M')
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
