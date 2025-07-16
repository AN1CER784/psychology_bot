from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def orm_add_model(session: AsyncSession, orm_model, data: dict):
    model = orm_model(**data)
    session.add(model)
    await session.commit()


async def orm_get_and_update_or_create_model(session: AsyncSession, orm_model, data: dict):
    query = select(orm_model).where(orm_model.id == data["id"])  # noqa
    result = await session.execute(query)
    model = result.scalar()
    if model:
        for key, value in data.items():
            setattr(model, key, value)
        await session.commit()
        return model
    else:
        model = orm_model(**data)
        session.add(model)
        await session.commit()
        return model


async def orm_get_all_models(session: AsyncSession, orm_model):
    query = select(orm_model)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_delete_model(session: AsyncSession, orm_model, data: dict):
    query = select(orm_model).where(orm_model.id == data["id"])  # noqa
    result = await session.execute(query)
    model = result.scalar()
    if not model:
        raise ValueError(f"Model with id {data['id']} not found")
    await session.delete(model)
    await session.commit()
