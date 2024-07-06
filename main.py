import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardRemove, BotCommand,
)

from handlers import register_user_commands, bot_commands
from config import TG_BOT_TOKEN, Form
from constants import TASK_INTERVAL_MINUTES, YOU_UNSUBSCRIBED_MESSAGE, \
    CHOSE_SUBSCRIBE_TYPE_MESSAGE, \
    PLEASE_AUTH_MESSAGE
from crud import get_users_by_filters, create_subscriber, subscribe_all, \
    subscribe_one_user, delete_all_subscriptions
from dependencies import UserCheckMiddleware, UserCheckRequired
from init_global_shedular import global_scheduler
from keyboards import yes_no_menu, auth_menu, subscribe_choice_menu
from logger_global import logger
from mail import make_periodical_tasks, set_bot_instance

form_router = Router()


# Отписаться от всех
@form_router.message(F.text.casefold() == "отписаться", UserCheckRequired())
async def unsubscribe_all(message: Message) -> None:
    await message.delete()
    await delete_all_subscriptions(int(message.from_user.id))

    await message.answer(
        YOU_UNSUBSCRIBED_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    )


# Отображение меню подписки
@form_router.message(F.text.casefold() == "подписаться", UserCheckRequired())
async def subscribe_start(message: Message, state: FSMContext, user_db: bool = False) -> None:
    await message.delete()

    # БД
    if user_db:
        await message.answer(
            CHOSE_SUBSCRIBE_TYPE_MESSAGE,
            reply_markup=subscribe_choice_menu(),
        )
    else:
        await message.answer(
            PLEASE_AUTH_MESSAGE,
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

    commands_for_bot = []
    for cmd in bot_commands:
        commands_for_bot.append(BotCommand(command=cmd[0], description=cmd[1]))

    bot = Bot(token=TG_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.set_my_commands(commands=commands_for_bot)
    dp = Dispatcher()
    dp.message.middleware(UserCheckMiddleware())
    dp.include_router(form_router)

    #
    register_user_commands(dp)

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
