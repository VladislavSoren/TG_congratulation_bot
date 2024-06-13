from aiogram.types import User, Chat

TEST_BOT_ID = 123

TEST_USER = User(id=123, is_bot=False, first_name='Test')

TEST_USER_CHAT = Chat(id=123, type='private', first_name=TEST_USER.first_name)
