from unittest.mock import AsyncMock

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove

from constants import START_MESSAGE, CANCEL_MESSAGE, REQUEST_NAME_MESSAGE_INVALID, REQUEST_NAME_MESSAGE
from main import command_start, cancel_handler, request_name, Form
from keyboards import main_menu
from tests.utils import TEST_BOT_ID, TEST_USER_CHAT, TEST_USER, TEST_MESSAGE


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
    message.text = "1"
    # message = TEST_MESSAGE
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER.id,
    ))
    await request_name(message, state)

    message.answer.assert_called_with(REQUEST_NAME_MESSAGE_INVALID, reply_markup=ReplyKeyboardRemove())


@pytest.mark.asyncio
async def test_request_name_valid():
    message = AsyncMock()
    message.text = "123"
    message.from_user.id = "123"
    # message = TEST_MESSAGE
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER.id,
    ))
    await request_name(message, state)

    assert await state.get_state() == Form.name.state
    assert (await state.get_data())["surname"] == message.text
    message.answer.assert_called_with(REQUEST_NAME_MESSAGE, reply_markup=ReplyKeyboardRemove())

