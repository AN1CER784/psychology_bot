from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from kbds.user_kb import headings_kb, first_heading_kb, third_heading_kb, second_heading_kb


user_router = Router()


@user_router.message(CommandStart())
async def start(message: Message, session: AsyncSession):
    """
    Приветствие при первом запуске

    :param message:
    :return:
    """
    await message.answer(
        "Приветствую вас, друзья! 👋\n\n"
        "Меня зовут Наталья Лукашова. 🌟\n\n"
        "Я семейный психолог с более чем 12-летним опытом работы с парами и отдельными партнерами. 🧠\n\n"
        "За все эти годы я убедилась: положительные изменения неизбежны, если есть желание их достичь. 🌈✨\n\n"
        "Каждая пара уникальна, и моя работа помогает раскрыть эту уникальность. 💑🔍\n\n"
        "Этот бот создан для того, чтобы помочь вам лучше понять себя и свои отношения. 🤖❤️\n\n"
        "Здесь я делюсь своим многолетним опытом и буду рада вашему участию! 🌟🙌\n\n"
        "Выбирайте рубрику, которая кажется вам наиболее интересной. 📚🔎\n\nИли же сразу запишитесь на консультацию✍️",
        reply_markup=await headings_kb(session, message.from_user.id))


@user_router.callback_query(F.data == "heading_1")
async def first_heading(callback: CallbackQuery):
    """
    Выбор первой рубрики

    :param callback:
    :return:
    """
    await callback.answer()
    await callback.message.edit_text("Можете выбрать то, что вас интересует по материалам рубрики\n"
                                     "<b>Трудности в построении отношений</b> 🧐", reply_markup=first_heading_kb)


@user_router.callback_query(F.data == "heading_2")
async def second_heading(callback: CallbackQuery):
    """
    Выбор первой рубрики

    :param callback:
    :return:
    """
    await callback.answer()
    await callback.message.edit_text("Можете выбрать то, что вас интересует по материалам рубрики\n"
                                     "<b>Как найти спутника жизни?</b> 💕", reply_markup=second_heading_kb)


@user_router.callback_query(F.data == "heading_3")
async def third_heading(callback: CallbackQuery):
    """
    Выбор первой рубрики

    :param callback:
    :return:
    """
    await callback.answer()
    await callback.message.edit_text(
        "<b>Cепарация</b> – это психологический процесс отделения ребенка от родителей, процесс становления отдельной самостоятельной и независимой личности\n\n"
        "Можете выбрать то, что вас интересует по материалам рубрики\n"
        "<b>Сепарация</b> ✂️", reply_markup=third_heading_kb)
