from unittest.mock import AsyncMock

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove

from constants import START_MESSAGE, CANCEL_MESSAGE, REQUEST_NAME_MESSAGE_INVALID
from main import command_start, cancel_handler, request_name
from keyboards import main_menu
from tests.utils import TEST_BOT_ID, TEST_USER_CHAT, TEST_USER


@pytest.mark.asyncio
async def test_start_handler():
    message = AsyncMock()
    await command_start(message)

    message.answer.assert_called_with(START_MESSAGE, reply_markup=main_menu())


@pytest.mark.asyncio
async def test_cancel_handler():
    message = AsyncMock()
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER.id,
    ))
    await cancel_handler(message, state)

    assert await state.get_state() is None
    message.delete.any_call()
    message.answer.assert_called_with(CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())


@pytest.mark.asyncio
async def test_request_name_invalid():
    message = AsyncMock()
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER.id,
    ))
    await request_name(message, state)

    message.answer.assert_called_with(REQUEST_NAME_MESSAGE_INVALID, reply_markup=ReplyKeyboardRemove())
