import asyncio

import schedule
from database.orm_query import orm_del_outdate_appointments


async def clear_db_on_time(session_pool):
    async with session_pool() as session:
        schedule.every().day.at("00:00").do(lambda: asyncio.create_task(orm_del_outdate_appointments(session=session)))
    while True:
        schedule.run_pending()
        await asyncio.sleep(30)
