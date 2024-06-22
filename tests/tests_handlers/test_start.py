from datetime import datetime
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy import text, exc, delete

from constants import START_MESSAGE, CANCEL_MESSAGE, SURNAME_INVALID_MESSAGE, ENTER_NAME_MESSAGE, \
    YOU_ALREADY_AUTH_MESSAGE, ENTER_SURNAME_MESSAGE, YOU_UNSUBSCRIBED_MESSAGE, BIRTHDAY_DATE_FORMAT, \
    ENTER_OTCHESTVO_MESSAGE, NAME_INVALID_MESSAGE, ENTER_BIRTHDAY_MESSAGE, OTCHESTVO_INVALID_MESSAGE, \
    CHECK_ENTERED_INFO_MESSAGE, BIRTHDAY_INVALID_MESSAGE
from db.db_helper import db_helper
from db.models import User
from main import command_start, cancel_handler, request_name, Form, request_surname, unsubscribe_all, request_otchestvo, \
    request_birthday, check_info
from keyboards import main_menu, subscribe_menu, yes_no_menu
from tests.utils import TEST_BOT_ID, TEST_USER_CHAT, TEST_USER, TEST_MESSAGE


# Тестирование функции command_start
@pytest.mark.asyncio
async def test_start_handler():
    message = AsyncMock()
    await command_start(message)

    message.answer.assert_called_with(START_MESSAGE, reply_markup=main_menu())


# Тестирование функции cancel_handler
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
    await message.delete.any_call()
    message.answer.assert_called_with(CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())


# Фикстура для подготовки тестовой базы данных
@pytest_asyncio.fixture
async def setup_and_teardown_db():
    # Создание данных в ДБ перед тестом
    async with db_helper.async_session_factory() as session:
        await session.execute(text('pragma foreign_keys=on'))

        user_info = {
            "birthday": '2000-05-05',
            "id_telegram": 333,
            "username_telegram": '123',
            "surname": '123',
            "name": '123',
            "otchestvo": '123'}

        # Prepare data
        birthday = datetime.strptime(str(user_info["birthday"]), BIRTHDAY_DATE_FORMAT)

        obj = User(
            id=int(user_info["id_telegram"]),
            username_telegram=user_info["username_telegram"],
            surname=user_info["surname"],
            name=user_info["name"],
            otchestvo=user_info["otchestvo"],
            birthday=birthday,
        )
        session.add(obj)

        await session.commit()
    # except exc.IntegrityError as e:
    #     await session.rollback()
    #     raise

    # Точка, где выполняется тест
    yield

    # Очистка данных после теста
    async with db_helper.async_session_factory() as session:
        stmt = delete(User).where(User.id == user_info["id_telegram"])
        await session.execute(stmt)
        await session.commit()


# Тестирование функции request_name
@pytest.mark.asyncio
async def test_unsubscribe_all(setup_and_teardown_db):
    message = AsyncMock()
    message.from_user.id = "123"

    await unsubscribe_all(message)

    await message.delete.any_call()
    message.answer.assert_called_with(YOU_UNSUBSCRIBED_MESSAGE, reply_markup=ReplyKeyboardRemove())


# Тестирование состояний функции request_surname
@pytest.mark.asyncio
async def test_request_surname_already_auth():
    message = AsyncMock()
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER.id,
    ))
    await request_surname(message, state, user_db=True)

    message.answer.assert_called_with(YOU_ALREADY_AUTH_MESSAGE, reply_markup=subscribe_menu())


@pytest.mark.asyncio
async def test_request_surname_not_auth():
    message = AsyncMock()
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER.id,
    ))
    await request_surname(message, state, user_db=False)

    message.answer.assert_called_with(ENTER_SURNAME_MESSAGE, reply_markup=ReplyKeyboardRemove())


# Тестирование состояний функции request_name
@pytest.mark.asyncio
async def test_request_name_valid():
    message = AsyncMock()
    message.text = "12"
    message.from_user.id = "12"
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER.id,
    ))
    await request_name(message, state)

    assert await state.get_state() == Form.name.state
    assert (await state.get_data())["surname"] == message.text
    message.answer.assert_called_with(ENTER_NAME_MESSAGE, reply_markup=ReplyKeyboardRemove())


@pytest.mark.asyncio
async def test_request_name_invalid():
    message = AsyncMock()
    message.text = "1"
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER.id,
    ))
    await state.set_state(Form.surname)

    await request_name(message, state)

    assert await state.get_state() == Form.surname.state
    message.answer.assert_called_with(SURNAME_INVALID_MESSAGE, reply_markup=ReplyKeyboardRemove())


# Тестирование состояний функции request_otchestvo
@pytest.mark.asyncio
async def test_request_otchestvo_valid():
    message = AsyncMock()
    message.text = "12"
    message.from_user.id = "12"
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER.id,
    ))
    await request_otchestvo(message, state)

    assert await state.get_state() == Form.otchestvo.state
    assert (await state.get_data())["name"] == message.text
    message.answer.assert_called_with(ENTER_OTCHESTVO_MESSAGE, reply_markup=ReplyKeyboardRemove())


@pytest.mark.asyncio
async def test_request_otchestvo_invalid():
    message = AsyncMock()
    message.text = "1"
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER.id,
    ))
    await state.set_state(Form.name)

    await request_otchestvo(message, state)

    assert await state.get_state() == Form.name.state
    message.answer.assert_called_with(NAME_INVALID_MESSAGE, reply_markup=ReplyKeyboardRemove())


# Тестирование состояний функции request_birthday

@pytest.mark.asyncio
async def test_request_birthday_valid():
    message = AsyncMock()
    message.text = "12"
    message.from_user.id = "12"
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER.id,
    ))
    await request_birthday(message, state)

    assert await state.get_state() == Form.birthday.state
    assert (await state.get_data())["otchestvo"] == message.text
    message.answer.assert_called_with(ENTER_BIRTHDAY_MESSAGE, reply_markup=ReplyKeyboardRemove())


@pytest.mark.asyncio
async def test_request_birthday_invalid():
    message = AsyncMock()
    message.text = "1"
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER.id,
    ))

    await request_birthday(message, state)

    message.answer.assert_called_with(OTCHESTVO_INVALID_MESSAGE, reply_markup=ReplyKeyboardRemove())


# Тестирование состояний функции check_info
@pytest.mark.asyncio
async def test_check_info_valid():
    message = AsyncMock()
    message.text = "2000-05-05"
    message.from_user.id = "12"
    surname = "12"
    name = "12"
    otchestvo = "12"
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER.id,
    ))

    await state.update_data(surname=surname)
    await state.update_data(name=name)
    await state.update_data(otchestvo=otchestvo)
    await state.update_data(birthday=message.text)

    await check_info(message, state)

    answer = f"ФИО: {surname} {name} {otchestvo}\nДата рождения: {message.text}"
    out_message = f"{CHECK_ENTERED_INFO_MESSAGE}\n{answer}"

    assert await state.get_state() == Form.check_info.state
    assert (await state.get_data())["birthday"] == message.text
    message.reply.assert_called_with(
        out_message,
        reply_markup=yes_no_menu())


@pytest.mark.asyncio
async def test_check_info_invalid():
    message = AsyncMock()
    message.text = "1"
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER.id,
    ))
    await state.set_state(Form.birthday)

    await check_info(message, state)

    assert await state.get_state() == Form.birthday.state
    message.answer.assert_called_with(BIRTHDAY_INVALID_MESSAGE, reply_markup=ReplyKeyboardRemove())
