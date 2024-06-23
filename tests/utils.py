from dataclasses import dataclass

from aiogram.types import User, Chat, Message
import time


@dataclass
class TestUserOk:
    __test__ = False
    surname: str = "12"
    name: str = "12"
    otchestvo: str = "12"
    birthday: str = "2000-05-05"


@dataclass
class TestUserBad:
    __test__ = False
    surname: str = "1"
    name: str = "1"
    otchestvo: str = "1"
    birthday: str = "2000-05"


TEST_BOT_ID = 123

TEST_USER_TG = User(id=123, is_bot=False, first_name='Test', username='12')

TEST_USER_CHAT = Chat(id=123, type='private', first_name=TEST_USER_TG.first_name)

TEST_MESSAGE = Message(message_id=1, date=time.time(), chat=TEST_USER_CHAT, from_user=TEST_USER_TG,
                       text="123")

# message_id: int
# """Unique message identifier inside this chat"""
# date: DateTime
# """Date the message was sent in Unix time. It is always a positive number, representing a valid date."""
# chat: Chat
