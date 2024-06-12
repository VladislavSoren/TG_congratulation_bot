from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')