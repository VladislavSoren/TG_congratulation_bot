from aiogram.types import User, Chat, Message
import time

TEST_BOT_ID = 123

TEST_USER = User(id=123, is_bot=False, first_name='Test')

TEST_USER_CHAT = Chat(id=123, type='private', first_name=TEST_USER.first_name)

TEST_MESSAGE = Message(message_id=1, date=time.time(), chat=TEST_USER_CHAT, from_user=TEST_USER,
                       text="123")

# message_id: int
# """Unique message identifier inside this chat"""
# date: DateTime
# """Date the message was sent in Unix time. It is always a positive number, representing a valid date."""
# chat: Chat