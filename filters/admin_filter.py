import os

from aiogram.filters import BaseFilter
from aiogram.types import Message

admin_ids = list(map(int, os.getenv("ADMIN_ID").split(",")))


class IsAdmin(BaseFilter):
    def __init__(self, *args, **kwargs) -> None:
        self.admin_ids = admin_ids

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids
