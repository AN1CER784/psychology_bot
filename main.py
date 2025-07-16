import asyncio
import logging

from aiogram import Dispatcher
from aiogram.types import BotCommandScopeAllPrivateChats

from common.bot_cmds_list import start
from config import bot
from database.clear_db import clear_db_on_time
from database.engine import create_db, session_maker
from database.orm_queries.schedule import orm_del_outdate_appointments
from filters.block_users_filter import IsFree
from handlers.admin.admin_activities_management import admin_router_activities_management
from handlers.admin.admin_add_test import admin_router_test
from handlers.admin.admin_add_topic import admin_router_topic
from handlers.admin.admin_main import admin_router
from handlers.admin.admin_schedule import admin_router_schedule
from handlers.admin.admin_users_management import admin_router_users_management
from handlers.back import admin_router_back, user_router_back
from handlers.user.user_consultation import user_router_consult
from handlers.user.user_on_start import user_router
from handlers.user.user_tests import user_router_test
from handlers.user.user_topic import user_router_topic
from handlers.user.user_watch_activity import user_router_activity
from middlewares.db import DataBaseSession

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

dp = Dispatcher()
dp.include_routers(admin_router_back, user_router, user_router_consult, user_router_topic, user_router_test,
                   user_router_activity, admin_router_schedule, admin_router_activities_management, admin_router_test,
                   admin_router_topic, admin_router_users_management, user_router_back, admin_router)
dp.callback_query.filter(IsFree(session_maker))
dp.message.filter(IsFree(session_maker))


async def on_startup(bot):
    await create_db()
    async with session_maker() as session:
        await orm_del_outdate_appointments(session)


async def on_shutdown(bot):
    logger.warning('Бот лег')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(
        commands=start,
        scope=BotCommandScopeAllPrivateChats()
    )
    await asyncio.gather(dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types()),
                         clear_db_on_time(session_maker))


if __name__ == "__main__":
    asyncio.run(main())
