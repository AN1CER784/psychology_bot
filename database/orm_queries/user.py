from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User

"""ORM QUERIES TO INSERT DATA"""


async def orm_update_user_status_by_id(session: AsyncSession, user_id: int, status: bool):
    query = update(User).where(User.id == user_id).values(status=status)
    await session.execute(query)
    await session.commit()


"""ORM QUERIES TO RETRIEVE DATA"""


async def orm_get_user_by_id(session: AsyncSession, user_id: int):
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    return result.scalar()
