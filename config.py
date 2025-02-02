import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

load_dotenv()
bot = Bot(os.getenv("TOKEN"), default=DefaultBotProperties(parse_mode="HTML"))
