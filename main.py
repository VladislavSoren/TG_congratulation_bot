import asyncio
import logging
from contextlib import suppress
from datetime import datetime, timedelta
from typing import Any

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
)
from sqlalchemy import exc

from config import TG_BOT_TOKEN
from constants import START_MESSAGE, SUBSCRIBE_OFFER, CANCEL_MESSAGE, REQUEST_NAME_MESSAGE_INVALID, \
    TASK_INTERVAL_MINUTES, AUTH_DATE_MESSAGE, REQUEST_NAME_MESSAGE, YOU_ALREADY_AUTH_MESSAGE
from crud import create_user, get_users_by_filters, create_subscriber, subscribe_all, \
    subscribe_one_user, delete_all_subscriptions
from dependencies import UserCheckMiddleware, UserCheckRequired
from init_global_shedular import global_scheduler
from keyboards import yes_no_menu, main_menu, auth_menu, subscribe_menu, subscribe_choice_menu
from mail import make_periodical_tasks, set_bot_instance
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


# Стартовое меню
@form_router.message(Command("start"))
async def command_start(message: Message) -> Any:
    return await message.answer(
        START_MESSAGE,
        reply_markup=main_menu()
    )


# Команда отмены
@form_router.message(F.text.casefold() == "отменить")
async def cancel_handler(message: Message, state: FSMContext) -> Any:
    """
    Позволяет юзеру отменить некое действие
    """
    current_state = await state.get_state()

    logger.info("Cancelling state %r", current_state)
    await state.clear()
    with suppress(Exception):
        await message.delete()

    return await message.answer(
        CANCEL_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    )


# Запрос фамилии
@form_router.message(F.text.casefold() == "авторизоваться", UserCheckRequired())
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
            "Введите свою фамилию",
            reply_markup=ReplyKeyboardRemove(),
        )


# Отписаться от всех
@form_router.message(F.text.casefold() == "отписаться", UserCheckRequired())
async def unsubscribe_all(message: Message) -> None:
    await message.delete()
    await delete_all_subscriptions(int(message.from_user.id))

    await message.answer(
        "Вы отписались от рассылки",
        reply_markup=ReplyKeyboardRemove(),
    )


# Запрос имени
@form_router.message(Form.surname)
async def request_name(message: Message, state: FSMContext) -> None:
    if len(message.text) > 1:
        await state.set_state(Form.name)
        await state.update_data(surname=message.text)
        await message.answer(
            REQUEST_NAME_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            REQUEST_NAME_MESSAGE_INVALID,
            reply_markup=ReplyKeyboardRemove(),
        )


# Запрос отчества
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


# Запрос дня рождения
@form_router.message(Form.otchestvo)
async def request_birthday(message: Message, state: FSMContext) -> None:
    if len(message.text) > 1:
        await state.set_state(Form.birthday)
        await state.update_data(otchestvo=message.text)
        await message.answer(
            AUTH_DATE_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            "Таких коротких отчеств не бывает, введите другое",
            reply_markup=ReplyKeyboardRemove(),
        )


# Проверка введённой информации
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


# Регистрация юзера после проверки инфы
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


# Возврат к первому шагу заполнения инфы, в следствие НЕ верных данных
@form_router.message(Form.check_info, F.text.casefold() == "нет")
async def check_info_no(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.surname)

    await message.answer(
        "Тогда попробуем ещё раз ввести данные.\nВведите свою фамилию",
        reply_markup=ReplyKeyboardRemove(),
    )


# Отображение меню подписки
@form_router.message(F.text.casefold() == "подписаться", UserCheckRequired())
async def subscribe_start(message: Message, state: FSMContext, user_db: bool = False) -> None:
    await message.delete()

    # БД
    if user_db:
        await message.answer(
            "Выберите тип подписки",
            reply_markup=subscribe_choice_menu(),
        )
    else:
        await message.answer(
            "Пройдите авторизацию",
            reply_markup=auth_menu(),
        )


# Подписание на ВСЕХ юзеров
@form_router.message(F.text.casefold() == "на всех")
async def subscribe_all_users(message: Message) -> None:
    # Добавляем юзера в таблицу подписчиков
    await create_subscriber(int(message.from_user.id))

    # Подписываемся на всех юзеров
    await subscribe_all(int(message.from_user.id))

    await message.answer(
        "Вы подписались на всех юзеров",
        reply_markup=subscribe_choice_menu(),
    )


@form_router.message(F.text.casefold() == "на конкретного пользователя")
async def request_surname_subscribe(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.surname_subscribe)

    # Добавляем юзера в таблицу подписчиков
    await create_subscriber(message.from_user.id)

    await message.answer(
        "Введите фамилию юзера",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Form.surname_subscribe)
async def request_name_subscribe(message: Message, state: FSMContext) -> None:
    # Получаем введённую фамилию
    surname = message.text.strip()
    await state.update_data(surname=surname)

    # Получаем юзеров из БД по фамилии
    users = await get_users_by_filters(surname=surname)
    await state.update_data(users=users)

    # Если юзеров НЕ нашлось -> введите повторно
    if len(users) == 0:
        await message.answer(
            "Юзеров с такой фамилией НЕ найдено, перепроверьте",
            reply_markup=ReplyKeyboardRemove(),
        )

    # Найден один -> предложение подписаться
    if len(users) == 1:
        user = users[0]
        await state.set_state(Form.subscribe_finish)
        await message.answer(
            f"Найден один юзер с такой фамилией: {user.surname} {user.name} {user.otchestvo}, подписаться?",
            reply_markup=yes_no_menu(),
        )

    # Найдено несколько -> следующий шаг фильтрации
    if len(users) > 1:
        await state.set_state(Form.name_subscribe)
        await message.answer(
            "Найдено несколько юзеров с такой фамилией, введите имя",
            reply_markup=ReplyKeyboardRemove(),
        )


@form_router.message(Form.name_subscribe)
async def request_otchestvo_subscribe(message: Message, state: FSMContext) -> None:
    # Получаем введённое имя
    name = message.text.strip()
    subscribe_info = await state.get_data()
    await state.update_data(name=name)

    # Получаем юзеров из БД по фильтрам
    users = await get_users_by_filters(surname=subscribe_info["surname"], name=name)
    await state.update_data(users=users)

    # Найден один -> предложение подписаться
    if len(users) == 1:
        user = users[0]
        await state.set_state(Form.subscribe_finish)
        await message.answer(
            f"Найден один юзер с такой фамилией: {user.surname} {user.name} {user.otchestvo}, подписаться?",
            reply_markup=yes_no_menu(),
        )

    # Найдено несколько -> следующий шаг фильтрации
    if len(users) > 1:
        await state.set_state(Form.otchestvo_subscribe)
        await message.answer(
            "Найдено несколько юзеров с такой фамилией и именем, введите отчество",
            reply_markup=ReplyKeyboardRemove(),
        )


@form_router.message(Form.otchestvo_subscribe)
async def subscribe_request(message: Message, state: FSMContext) -> None:
    # Получаем введённое отчество
    otchestvo = message.text.strip()
    subscribe_info = await state.get_data()
    await state.update_data(otchestvo=otchestvo)

    # Получаем юзеров из БД по фильтрам
    users = await get_users_by_filters(
        surname=subscribe_info["surname"],
        name=subscribe_info["name"],
        otchestvo=otchestvo)
    await state.update_data(users=users)

    # Найден один -> предложение подписаться
    if len(users) == 1:
        user = users[0]
        await state.set_state(Form.subscribe_finish)
        await message.answer(
            f"Найден один юзер с такой фамилией: {user.surname} {user.name} {user.otchestvo}, подписаться?",
            reply_markup=yes_no_menu(),
        )

    # Найдено несколько -> следующий шаг фильтрации
    if len(users) > 1:
        await state.set_state(Form.subscribe_finish)
        await message.answer(
            "Найдено несколько юзеров с данным ФИО, подписаться на всех?",
            reply_markup=ReplyKeyboardRemove(),
        )


@form_router.message(Form.subscribe_finish, F.text.casefold() == "да")
async def subscribe_finish_ok(message: Message, state: FSMContext) -> None:
    # Подписываем на найденного юзера в БД
    subscribe_info = await state.get_data()

    await subscribe_one_user(int(message.from_user.id), subscribe_info["users"])

    await state.clear()

    await message.delete()

    await message.answer(
        "Подписка оформлена",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Form.subscribe_finish, F.text.casefold() == "нет")
async def subscribe_finish_no(message: Message, state: FSMContext) -> None:
    await state.clear()

    await message.delete()

    await message.answer(
        "Подписка отклонена",
        reply_markup=ReplyKeyboardRemove(),
    )


async def main():
    global bot

    await startup()

    bot = Bot(token=TG_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.message.middleware(UserCheckMiddleware())
    dp.include_router(form_router)

    # Передача объекта Bot в mail.py
    set_bot_instance(bot)

    await dp.start_polling(bot)


async def startup():
    current_time = datetime.now()
    task_execute_date = (current_time + timedelta(days=0)).replace(
        hour=0, minute=0, second=0, microsecond=0)

    try:
        global_scheduler.add_job(
            make_periodical_tasks,
            id="trigger_task",
            trigger="cron",
            minute=f"*/{TASK_INTERVAL_MINUTES}",
            start_date=task_execute_date.strftime("%Y-%m-%d %H:%M:%S"),
            misfire_grace_time=60,
        )

        logger.info(f"scheduler main.py id - {id(global_scheduler)}")
        global_scheduler.start()  # Necessarily to add periodical task before scheduler start!
        global_scheduler.print_jobs()

    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    logger.info(f"Start bot")
    asyncio.run(main())
    logger.info(f"Finish bot")
