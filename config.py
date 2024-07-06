from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')

DB_URL = 'sqlite+aiosqlite:///./storage.db'
DB_ECHO: bool = True


class Form(StatesGroup):
    surname = State()
    name = State()
    otchestvo = State()
    birthday = State()
    check_info = State()
    surname_subscribe = State()
    name_subscribe = State()
    otchestvo_subscribe = State()
    subscribe_finish = State()
