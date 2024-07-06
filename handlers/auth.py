from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from constants import YOU_ALREADY_AUTH_MESSAGE, ENTER_SURNAME_MESSAGE, ENTER_NAME_MESSAGE, SURNAME_INVALID_MESSAGE, \
    ENTER_OTCHESTVO_MESSAGE, NAME_INVALID_MESSAGE, ENTER_BIRTHDAY_MESSAGE, OTCHESTVO_INVALID_MESSAGE, \
    CHECK_ENTERED_INFO_MESSAGE, BIRTHDAY_INVALID_MESSAGE, SUBSCRIBE_OFFER, REPEAT_AUTHORIZATION_MESSAGE
from crud import create_user
from keyboards import subscribe_menu, yes_no_menu
from config import Form
from validators import is_valid_date


# Запрос фамилии
async def request_surname(message: Message, state: FSMContext, user_db: bool = False) -> None:
    await message.delete()

    if user_db:
        await message.answer(
            YOU_ALREADY_AUTH_MESSAGE,
            reply_markup=subscribe_menu()
        )
    else:
        await state.set_state(Form.surname)

        await message.answer(
            ENTER_SURNAME_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )


# Запрос имени
# @form_router.message(Form.surname)
async def request_name(message: Message, state: FSMContext) -> None:
    if len(message.text) > 1:
        await state.set_state(Form.name)
        await state.update_data(surname=message.text)
        await message.answer(
            ENTER_NAME_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            SURNAME_INVALID_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )


# Запрос отчества
async def request_otchestvo(message: Message, state: FSMContext) -> None:
    if len(message.text) > 1:
        await state.set_state(Form.otchestvo)
        await state.update_data(name=message.text)
        await message.answer(
            ENTER_OTCHESTVO_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            NAME_INVALID_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )


# Запрос дня рождения
async def request_birthday(message: Message, state: FSMContext) -> None:
    if len(message.text) > 1:
        await state.set_state(Form.birthday)
        await state.update_data(otchestvo=message.text)
        await message.answer(
            ENTER_BIRTHDAY_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            OTCHESTVO_INVALID_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )


# Проверка введённой информации
async def check_info(message: Message, state: FSMContext) -> None:
    date_is_valid = is_valid_date(message.text)

    if date_is_valid:
        await state.set_state(Form.check_info)
        await state.update_data(birthday=message.text)

        data = await state.get_data()
        surname = data["surname"]
        name = data["name"]
        otchestvo = data["otchestvo"]
        birthday = data["birthday"]
        answer = f"ФИО: {surname} {name} {otchestvo}\nДата рождения: {birthday}"

        await message.reply(
            f"{CHECK_ENTERED_INFO_MESSAGE}\n{answer}",
            reply_markup=yes_no_menu(),
        )
    else:
        await message.answer(
            BIRTHDAY_INVALID_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )


# Регистрация юзера после проверки инфы
async def check_info_yes(message: Message, state: FSMContext) -> None:
    await message.delete()

    user_info = await state.get_data()

    user_info["id_telegram"] = message.from_user.id
    user_info["username_telegram"] = message.from_user.username

    # Запрос на занесение юзера в БД
    await create_user(user_info)

    await state.clear()
    await message.answer(
        SUBSCRIBE_OFFER,
        reply_markup=subscribe_menu(),
    )


# Возврат к первому шагу заполнения инфы, в следствие НЕ верных д
async def check_info_no(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.surname)

    await message.answer(
        REPEAT_AUTHORIZATION_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    )
