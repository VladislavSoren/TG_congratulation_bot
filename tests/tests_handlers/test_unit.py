from datetime import datetime
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy import text, delete

from constants import START_MESSAGE, CANCEL_MESSAGE, SURNAME_INVALID_MESSAGE, ENTER_NAME_MESSAGE, \
    YOU_ALREADY_AUTH_MESSAGE, ENTER_SURNAME_MESSAGE, YOU_UNSUBSCRIBED_MESSAGE, BIRTHDAY_DATE_FORMAT, \
    ENTER_OTCHESTVO_MESSAGE, NAME_INVALID_MESSAGE, ENTER_BIRTHDAY_MESSAGE, OTCHESTVO_INVALID_MESSAGE, \
    CHECK_ENTERED_INFO_MESSAGE, BIRTHDAY_INVALID_MESSAGE, SUBSCRIBE_OFFER, REPEAT_AUTHORIZATION_MESSAGE, \
    CHOSE_SUBSCRIBE_TYPE_MESSAGE, PLEASE_AUTH_MESSAGE
from db.db_helper import db_helper
from db.models import User
from main import unsubscribe_all, subscribe_start
from config import Form
from handlers.auth import request_surname, request_name, request_otchestvo, request_birthday, check_info, \
    check_info_yes, check_info_no
from handlers.commands import command_start, cancel_handler
from keyboards import main_menu, subscribe_menu, yes_no_menu, subscribe_choice_menu, auth_menu
from tests.utils import TEST_BOT_ID, TEST_USER_CHAT, TEST_USER_TG, TestUserOk, TestUserBad


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
        user_id=TEST_USER_TG.id,
    ))
    await cancel_handler(message, state)

    assert await state.get_state() is None
    await message.delete.any_call()
    message.answer.assert_called_with(CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())


# Фикстура для подготовки тестовой базы данных
@pytest_asyncio.fixture(scope="function")
async def setup_and_teardown_db():
    # Создание данных в ДБ перед тестом
    async with db_helper.async_session_factory() as session:
        await session.execute(text('pragma foreign_keys=on'))

        # Prepare data
        birthday = datetime.strptime(str(TestUserOk.birthday), BIRTHDAY_DATE_FORMAT)

        obj = User(
            id=TEST_USER_TG.id,
            username_telegram=TEST_USER_TG.username,
            surname=TestUserOk.surname,
            name=TestUserOk.name,
            otchestvo=TestUserOk.otchestvo,
            birthday=birthday,
        )
        session.add(obj)

        await session.commit()

    # Точка, где выполняется тест
    yield

    # Очистка данных после теста
    async with db_helper.async_session_factory() as session:
        stmt = delete(User).where(User.id == TEST_USER_TG.id)
        await session.execute(stmt)
        await session.commit()


# Тестирование функции request_name
@pytest.mark.asyncio
async def test_unsubscribe_all(setup_and_teardown_db):
    message = AsyncMock()
    message.from_user.id = TEST_USER_TG.id

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
        user_id=TEST_USER_TG.id,
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
        user_id=TEST_USER_TG.id,
    ))
    await request_surname(message, state, user_db=False)

    message.answer.assert_called_with(ENTER_SURNAME_MESSAGE, reply_markup=ReplyKeyboardRemove())


# Тестирование состояний функции request_name
@pytest.mark.asyncio
async def test_request_name_valid():
    message = AsyncMock()
    message.text = TestUserOk.surname
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER_TG.id,
    ))
    await request_name(message, state)

    assert await state.get_state() == Form.name.state
    assert (await state.get_data())["surname"] == message.text
    message.answer.assert_called_with(ENTER_NAME_MESSAGE, reply_markup=ReplyKeyboardRemove())


@pytest.mark.asyncio
async def test_request_name_invalid():
    message = AsyncMock()
    message.text = TestUserBad.surname
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER_TG.id,
    ))
    await state.set_state(Form.surname)

    await request_name(message, state)

    assert await state.get_state() == Form.surname.state
    message.answer.assert_called_with(SURNAME_INVALID_MESSAGE, reply_markup=ReplyKeyboardRemove())


# Тестирование состояний функции request_otchestvo
@pytest.mark.asyncio
async def test_request_otchestvo_valid():
    message = AsyncMock()
    message.text = TestUserOk.name
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER_TG.id,
    ))
    await request_otchestvo(message, state)

    assert await state.get_state() == Form.otchestvo.state
    assert (await state.get_data())["name"] == message.text
    message.answer.assert_called_with(ENTER_OTCHESTVO_MESSAGE, reply_markup=ReplyKeyboardRemove())


@pytest.mark.asyncio
async def test_request_otchestvo_invalid():
    message = AsyncMock()
    message.text = TestUserBad.name
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER_TG.id,
    ))
    await state.set_state(Form.name)

    await request_otchestvo(message, state)

    assert await state.get_state() == Form.name.state
    message.answer.assert_called_with(NAME_INVALID_MESSAGE, reply_markup=ReplyKeyboardRemove())


# Тестирование состояний функции request_birthday

@pytest.mark.asyncio
async def test_request_birthday_valid():
    message = AsyncMock()
    message.text = TestUserOk.otchestvo
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER_TG.id,
    ))
    await request_birthday(message, state)

    assert await state.get_state() == Form.birthday.state
    assert (await state.get_data())["otchestvo"] == message.text
    message.answer.assert_called_with(ENTER_BIRTHDAY_MESSAGE, reply_markup=ReplyKeyboardRemove())


@pytest.mark.asyncio
async def test_request_birthday_invalid():
    message = AsyncMock()
    message.text = TestUserBad.surname
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER_TG.id,
    ))

    await request_birthday(message, state)

    message.answer.assert_called_with(OTCHESTVO_INVALID_MESSAGE, reply_markup=ReplyKeyboardRemove())


# Тестирование состояний функции check_info
@pytest.mark.asyncio
async def test_check_info_valid():
    message = AsyncMock()
    message.text = TestUserOk.birthday
    message.from_user.id = TEST_USER_TG.id
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER_TG.id,
    ))

    await state.update_data(surname=TestUserOk.surname)
    await state.update_data(name=TestUserOk.name)
    await state.update_data(otchestvo=TestUserOk.otchestvo)
    await state.update_data(birthday=TestUserOk.birthday)

    await check_info(message, state)

    answer = f"ФИО: {TestUserOk.surname} {TestUserOk.name} {TestUserOk.otchestvo}\nДата рождения: {message.text}"
    out_message = f"{CHECK_ENTERED_INFO_MESSAGE}\n{answer}"

    assert await state.get_state() == Form.check_info.state
    assert (await state.get_data())["birthday"] == message.text
    message.reply.assert_called_with(
        out_message,
        reply_markup=yes_no_menu())


@pytest.mark.asyncio
async def test_check_info_invalid():
    message = AsyncMock()
    message.text = TestUserBad.birthday
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER_TG.id,
    ))
    await state.set_state(Form.birthday)

    await check_info(message, state)

    assert await state.get_state() == Form.birthday.state
    message.answer.assert_called_with(BIRTHDAY_INVALID_MESSAGE, reply_markup=ReplyKeyboardRemove())


# Тестирование состояний функции check_info_yes
# Фикстура для удаления созданного юзера
@pytest_asyncio.fixture(scope="function")
async def delete_created_user_in_db():
    # Точка ДО выполнения теста

    # Точка, где выполняется тест
    yield

    id_telegram = TEST_USER_TG.id

    # Очистка данных после теста
    async with db_helper.async_session_factory() as session:
        stmt = delete(User).where(User.id == id_telegram)
        await session.execute(stmt)
        await session.commit()


@pytest.mark.asyncio
async def test_check_info_yes(delete_created_user_in_db):
    message = AsyncMock()
    message.from_user.id = TEST_USER_TG.id
    message.from_user.username = TEST_USER_TG.username

    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER_TG.id,
    ))

    await state.update_data(surname=TestUserOk.surname)
    await state.update_data(name=TestUserOk.name)
    await state.update_data(otchestvo=TestUserOk.otchestvo)
    await state.update_data(birthday=TestUserOk.birthday)
    await state.set_state(Form.check_info)

    await check_info_yes(message, state)

    await message.delete.any_call()
    assert await state.get_state() is None
    message.answer.assert_called_with(SUBSCRIBE_OFFER, reply_markup=subscribe_menu())


# Тестирование состояний функции check_info_no
@pytest.mark.asyncio
async def test_check_info_no():
    message = AsyncMock()
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER_TG.id,
    ))
    await state.set_state(Form.surname)

    await check_info_no(message, state)

    assert await state.get_state() == Form.surname.state
    message.answer.assert_called_with(REPEAT_AUTHORIZATION_MESSAGE, reply_markup=ReplyKeyboardRemove())


# Тестирование состояний функции subscribe_start
@pytest.mark.asyncio
async def test_subscribe_start_already_auth():
    message = AsyncMock()
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER_TG.id,
    ))
    await subscribe_start(message, state, user_db=True)

    await message.delete.any_call()
    message.answer.assert_called_with(CHOSE_SUBSCRIBE_TYPE_MESSAGE, reply_markup=subscribe_choice_menu())


@pytest.mark.asyncio
async def test_subscribe_start_auth():
    message = AsyncMock()
    storage = MemoryStorage()

    state = FSMContext(storage=storage, key=StorageKey(
        bot_id=TEST_BOT_ID,
        chat_id=TEST_USER_CHAT.id,
        user_id=TEST_USER_TG.id,
    ))
    await subscribe_start(message, state, user_db=False)

    await message.delete.any_call()
    message.answer.assert_called_with(PLEASE_AUTH_MESSAGE, reply_markup=auth_menu())
