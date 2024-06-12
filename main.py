import asyncio
import logging

from aiogram import Bot, Dispatcher, Router, F, MagicFilter
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from config import TG_BOT_TOKEN
from constants import START_MESSAGE, SUBSCRIBE_OFFER
from validators import is_valid_date

# Параметры логирования
logging.basicConfig(filename="py_log.log",
                    filemode="w",
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

form_router = Router()


class Form(StatesGroup):
    surname = State()
    name = State()
    otchestvo = State()
    birthday = State()
    check_info = State()


def yes_no_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Да"),
                KeyboardButton(text="Нет"),
            ]
        ],
        resize_keyboard=True,
    )


def auth_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Авторизоваться"),
                KeyboardButton(text="Отменить"),
            ]
        ],
        resize_keyboard=True,
    )


def subscribe_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Подписаться")
            ]
        ],
        resize_keyboard=True,
    )


def subscribe_choice_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="На всех"),
                KeyboardButton(text="На конкретного пользователя"),
            ]
        ],
        resize_keyboard=True,
    )


@form_router.message(Command("start"))
async def command_start(message: Message) -> None:
    await message.answer(
        START_MESSAGE,
        reply_markup=auth_menu()
    )


@form_router.message(F.text.casefold() == "отменить")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to Отменить any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )


# @form_router.message(F.text.casefold() == "Да")
@form_router.message(F.text.casefold() == "авторизоваться")
async def request_surname(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.surname)

    await message.reply(
        "Введите свою фамилию",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Form.surname)
async def request_name(message: Message, state: FSMContext) -> None:
    if len(message.text) > 1:
        await state.set_state(Form.name)
        await state.update_data(surname=message.text)
        await message.reply(
            "Отлично, теперь введите ваше имя",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.reply(
            "Таких коротких фамилий не бывает, введите другую",
            reply_markup=ReplyKeyboardRemove(),
        )


@form_router.message(Form.name)
async def request_otchestvo(message: Message, state: FSMContext) -> None:
    if len(message.text) > 1:
        await state.set_state(Form.otchestvo)
        await state.update_data(name=message.text)
        await message.reply(
            "Отлично, теперь введите ваше отчество",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.reply(
            "Таких коротких имён не бывает, введите другое",
            reply_markup=ReplyKeyboardRemove(),
        )


@form_router.message(Form.otchestvo)
async def request_birthday(message: Message, state: FSMContext) -> None:
    if len(message.text) > 1:
        await state.set_state(Form.birthday)
        await state.update_data(otchestvo=message.text)
        await message.reply(
            "Отлично, теперь введите дату вашего рождения, в формате\n14.09.1985",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.reply(
            "Таких коротких отчеств не бывает, введите другое",
            reply_markup=ReplyKeyboardRemove(),
        )


@form_router.message(Form.birthday)
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
            f"Отлично, проверьте корректность введённой информации:\n{answer}",
            reply_markup=yes_no_menu(),
        )
    else:
        await message.reply(
            "Дата введена неверно, пожалуйста перепроверьте",
            reply_markup=ReplyKeyboardRemove(),
        )


@form_router.message(Form.check_info, F.text.casefold() == "да")
async def check_info_yes(message: Message, state: FSMContext) -> None:
    await state.clear()

    await message.reply(
        SUBSCRIBE_OFFER,
        reply_markup=subscribe_menu(),
    )


@form_router.message(Form.check_info, F.text.casefold() == "нет")
async def check_info_no(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.surname)

    await message.reply(
        "Тогда попробуем ещё раз ввести данные.\nВведите свою фамилию",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(F.text.casefold() == "подписаться")
async def subscribe_start(message: Message, state: FSMContext) -> None:
    if len(message.text) > 1:
        await state.set_state(Form.birthday)
        await state.update_data(otchestvo=message.text)
        await message.reply(
            "Отлично, теперь введите дату вашего рождения, в формате\n14.09.1985",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.reply(
            "Таких коротких отчеств не бывает, введите другое",
            reply_markup=ReplyKeyboardRemove(),
        )


async def main():
    bot = Bot(token=TG_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.warning(f"Start bot")
    asyncio.run(main())
    logging.warning(f"Finish bot")
