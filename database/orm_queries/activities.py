from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import ActualActivity, Topic, Test

"""ORM QUERIES TO RETRIEVE DATA"""


async def orm_get_activity_by_title(session: AsyncSession, title: str, model):
    query = select(model).where(model.title == title) # noqa
    result = await session.execute(query)
    return result.scalar()


async def orm_get_actual_activity(session: AsyncSession):
    query = (
        select(ActualActivity)
        .options(selectinload(ActualActivity.topic), selectinload(ActualActivity.test))
    )
    result = await session.execute(query)
    activity = result.scalar()
    if activity is not None:
        if activity.topic is not None:
            return {
                "type": "topic",
                "object": activity.topic
            }
        elif activity.test is not None:
            return {
                "type": "test",
                "object": activity.test
            }


async def orm_get_activity_items_by_id(session: AsyncSession, model, model_id):
    """Returns all related topic_items or test_items for the given topic/test"""
    query = (
        select(model)
        .where(model.id == model_id) # noqa
        .options(selectinload(model.items))
    )
    result = await session.execute(query)
    obj = result.scalar_one_or_none()
    if obj:
        return obj.items
    return []

"""ORM QUERIES TO INSERT DATA"""
