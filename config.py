from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')

DB_URL = 'sqlite+aiosqlite:///./storage.db'
DB_ECHO: bool = True
