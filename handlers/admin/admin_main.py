from aiogram import F, Router
from aiogram.types import CallbackQuery

from filters.admin_filter import IsAdmin
from kbds.admin_kb import admin_kb

admin_router = Router()
admin_router.message.filter(IsAdmin())


@admin_router.callback_query(F.data == "admin_panel")
async def admin(callback: CallbackQuery):
    """
    Open admin panel

    :param callback:
    :return:
    """
    await callback.answer()
    await callback.message.edit_text("Вы вошли в админ панель", reply_markup=admin_kb)
