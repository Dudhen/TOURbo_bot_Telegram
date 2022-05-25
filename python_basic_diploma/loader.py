import os
import telebot
from dotenv import load_dotenv
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE


load_dotenv(
    dotenv_path=r'.evn',
    verbose=True)

bot = telebot.TeleBot(os.getenv('TOKEN'))

my_calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1_callback = CallbackData("Мой календарь", "action", "year", "month", "day")