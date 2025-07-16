from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker

from database.orm_queries.user import orm_get_user_by_id


class IsFree(BaseFilter):
    def __init__(self, session_pool: async_sessionmaker, *args, **kwargs) -> None:
        self.session_pool = session_pool

    async def __call__(
            self,
            message: Message = None
    ) -> bool:
        async with self.session_pool() as session:
            if hasattr(message, 'chat'):
                user = await orm_get_user_by_id(session, message.chat.id)
            else:
                user = await orm_get_user_by_id(session, message.from_user.id)
            if not user:
                return True
            elif user.status:
                return True
