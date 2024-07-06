import pytest
import pytest_asyncio
from aiogram import Dispatcher, Router
from aiogram.filters import Command
from aiogram.fsm.storage.base import StorageKey

from main import command_start
from tests.mocked_bot import MockedBot
from tests.utils import TEST_USER_CHAT, TEST_USER_TG, TEST_BOT_ID


@pytest.fixture()
def bot():
    return MockedBot()


@pytest_asyncio.fixture(name="storage_key")
def create_storage_key(bot: MockedBot):
    return StorageKey(chat_id=TEST_USER_CHAT.id, user_id=TEST_USER_TG.id, bot_id=TEST_BOT_ID)


def register_user_handlers(router: Router) -> None:
    router.message.register(command_start, Command("start"))


@pytest_asyncio.fixture()
async def dispatcher():
    dp = Dispatcher()
    register_user_handlers(dp)
    await dp.emit_startup()
    try:
        yield dp
    finally:
        await dp.emit_shutdown()
