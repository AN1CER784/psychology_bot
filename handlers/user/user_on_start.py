from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from kbds.user_kb import get_main_kb

user_router = Router()


@user_router.message(CommandStart())
async def start(message: Message, session: AsyncSession):
    """
    First message when start
    """
    await message.answer(
        "Приветствую вас, друзья! 👋\n\n"
        "Меня зовут Наталья Лукашова. 🌟\n\n"
        "Я семейный психолог с более чем 12-летним опытом работы с парами и отдельными партнерами. 🧠\n\n"
        "За все эти годы я убедилась: положительные изменения неизбежны, если есть желание их достичь. 🌈✨\n\n"
        "Каждая пара уникальна, и моя работа помогает раскрыть эту уникальность. 💑🔍\n\n"
        "Этот бот создан для того, чтобы помочь вам лучше понять себя и свои отношения. 🤖❤️\n\n"
        "Здесь я делюсь своим многолетним опытом и буду рада вашему участию! 🌟🙌\n\n"
        "Нажмите начать для прохождения активности✍️",
        reply_markup=await get_main_kb(session, message.from_user.id))
