from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from kbds.admin_kb import admin_kb
from handlers.user.user_on_start import start

admin_router_back = Router()
user_router_back = Router()


@admin_router_back.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery):
    """
    Go back to main admin panel
    :param callback:
    :return:
    """
    await callback.answer()
    await callback.message.edit_text("Вы в панели админа", reply_markup=admin_kb)


@user_router_back.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, session: AsyncSession):
    """
    back to main menu
    """
    await callback.answer()
    await callback.message.delete()
    await start(callback.message, session)
