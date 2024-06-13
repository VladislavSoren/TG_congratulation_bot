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
from sqlalchemy import exc

from config import TG_BOT_TOKEN
from constants import START_MESSAGE, SUBSCRIBE_OFFER
from crud import create_user, get_user_by_telegram_id
from validators import is_valid_date

logger = logging.getLogger(__name__)

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
    surname_subscribe = State()
    name_subscribe = State()
    otchestvo_subscribe = State()
    subscribe_finish = State()


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


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Авторизоваться"),
                KeyboardButton(text="Подписаться"),
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
        reply_markup=main_menu()
    )


@form_router.message(F.text.casefold() == "отменить")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to Отменить any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logger.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(F.text.casefold() == "авторизоваться")
async def request_surname(message: Message, state: FSMContext) -> None:

    user_db = await get_user_by_telegram_id(message.from_user.id)

    if user_db:
        await message.answer(
            "Вы уже авторизованы",
            reply_markup=subscribe_menu()
        )
    else:
        await state.set_state(Form.surname)

        await message.answer(
            "Введите свою фамилию",
            reply_markup=ReplyKeyboardRemove(),
        )


@form_router.message(Form.surname)
async def request_name(message: Message, state: FSMContext) -> None:
    if len(message.text) > 1:
        await state.set_state(Form.name)
        await state.update_data(surname=message.text)
        await message.answer(
            "Отлично, теперь введите ваше имя",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            "Таких коротких фамилий не бывает, введите другую",
            reply_markup=ReplyKeyboardRemove(),
        )


@form_router.message(Form.name)
async def request_otchestvo(message: Message, state: FSMContext) -> None:
    if len(message.text) > 1:
        await state.set_state(Form.otchestvo)
        await state.update_data(name=message.text)
        await message.answer(
            "Отлично, теперь введите ваше отчество",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            "Таких коротких имён не бывает, введите другое",
            reply_markup=ReplyKeyboardRemove(),
        )


@form_router.message(Form.otchestvo)
async def request_birthday(message: Message, state: FSMContext) -> None:
    if len(message.text) > 1:
        await state.set_state(Form.birthday)
        await state.update_data(otchestvo=message.text)
        await message.answer(
            "Отлично, теперь введите дату вашего рождения, в формате\n14.09.1985",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
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
    user_info = await state.get_data()

    user_info["id_telegram"] = message.from_user.id
    user_info["username_telegram"] = message.from_user.username

    # Запрос на занесение юзера в БД
    try:
        await create_user(user_info)
    except exc.IntegrityError as e:
        await message.answer(
            str(e),
            reply_markup=subscribe_menu(),
        )
        logger.error(e)
    else:
        await state.clear()
        await message.answer(
            SUBSCRIBE_OFFER,
            reply_markup=subscribe_menu(),
        )


@form_router.message(Form.check_info, F.text.casefold() == "нет")
async def check_info_no(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.surname)

    await message.answer(
        "Тогда попробуем ещё раз ввести данные.\nВведите свою фамилию",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(F.text.casefold() == "подписаться")
async def subscribe_start(message: Message) -> None:
    await message.answer(
        "Выберите тип подписки",
        reply_markup=subscribe_choice_menu(),
    )


@form_router.message(F.text.casefold() == "на всех")
async def subscribe_all(message: Message) -> None:
    # Запрос на подписание на ВСЕХ юзеров

    await message.answer(
        "Вы подписались на всех юзеров",
        reply_markup=subscribe_choice_menu(),
    )


@form_router.message(F.text.casefold() == "на конкретного пользователя")
async def request_surname_subscribe(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.surname_subscribe)

    await message.answer(
        "Введите фамилию юзера",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Form.surname_subscribe)
async def request_name_subscribe(message: Message, state: FSMContext) -> None:
    # Получаем юзеров из БД по фамилии

    no_users = True
    one_user = True
    several_users = True

    if no_users:
        await message.answer(
            "Юзеров с такой фамилией НЕ найдено, перепроверьте",
            reply_markup=ReplyKeyboardRemove(),
        )

    if one_user:
        await state.set_state(Form.subscribe_finish)
        await message.answer(
            "Найден один юзер с такой фамилией, его ФИО, подписаться?",
            reply_markup=yes_no_menu(),
        )

    if several_users:
        await state.set_state(Form.name_subscribe)
        await message.answer(
            "Найдено несколько юзеров с такой фамилией, введите имя",
            reply_markup=ReplyKeyboardRemove(),
        )

    # await state.set_state(Form.name)
    # await state.update_data(surname=message.text)


@form_router.message(Form.name_subscribe)
async def request_otchestvo_subscribe(message: Message, state: FSMContext) -> None:
    # По аналогии

    await message.answer(
        "Таких коротких имён не бывает, введите другое",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Form.otchestvo_subscribe)
async def subscribe_finish(message: Message, state: FSMContext) -> None:
    # По аналогии

    await message.answer(
        "Таких коротких имён не бывает, введите другое",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Form.subscribe_finish)
async def subscribe_finish(message: Message, state: FSMContext) -> None:
    # Подписываем на найденного юзера в БД

    await state.clear()

    await message.answer(
        "Таких коротких имён не бывает, введите другое",
        reply_markup=ReplyKeyboardRemove(),
    )


async def main():
    bot = Bot(token=TG_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.warning(f"Start bot")
    asyncio.run(main())
    logger.warning(f"Finish bot")
