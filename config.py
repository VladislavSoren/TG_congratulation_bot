from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')

DB_URL = 'sqlite+aiosqlite:///./storage.db'
DB_ECHO: bool = True

# id = 1888466032
# is_bot = False
# first_name = 'Vlad'
# last_name = None
# username = 'VladislavSoren'
# language_code = 'ru'
# is_premium = None
# added_to_attachment_menu = None
# can_join_groups = None
# can_read_all_group_messages = None
# supports_inline_queries = None
# can_connect_to_business = None

# (builtins.TypeError)
# SQLite
# Date
# type
# only
# accepts
# Python
# date
# objects as input.
# [SQL: INSERT
# INTO
# user(id_telegram, username_telegram, surname, name, otchestvo, birthday)
# VALUES(?, ?, ?, ?, ?, ?)]
# [parameters: [{'username_telegram': 'VladislavSoren', 'surname': '12', 'otchestvo': '12', 'birthday': '14.09.1985',
#                'id_telegram': 1888466032, 'name': '12'}]]
