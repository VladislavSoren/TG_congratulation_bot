from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from config import Form
from constants import YOU_UNSUBSCRIBED_MESSAGE, CHOSE_SUBSCRIBE_TYPE_MESSAGE, PLEASE_AUTH_MESSAGE
from db.crud import delete_all_subscriptions, create_subscriber, subscribe_all, get_users_by_filters, subscribe_one_user
from keyboards import subscribe_choice_menu, auth_menu, yes_no_menu


# Отписаться от всех
async def unsubscribe_all(message: Message) -> None:
    await message.delete()
    await delete_all_subscriptions(int(message.from_user.id))

    await message.answer(
        YOU_UNSUBSCRIBED_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    )


# Отображение меню подписки
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
async def subscribe_all_users(message: Message) -> None:
    # Добавляем юзера в таблицу подписчиков
    await create_subscriber(int(message.from_user.id))

    # Подписываемся на всех юзеров
    await subscribe_all(int(message.from_user.id))

    await message.answer(
        "Вы подписались на всех юзеров",
        reply_markup=subscribe_choice_menu(),
    )


async def request_surname_subscribe(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.surname_subscribe)

    # Добавляем юзера в таблицу подписчиков
    await create_subscriber(message.from_user.id)

    await message.answer(
        "Введите фамилию юзера",
        reply_markup=ReplyKeyboardRemove(),
    )


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


async def subscribe_finish_no(message: Message, state: FSMContext) -> None:
    await state.clear()

    await message.delete()

    await message.answer(
        "Подписка отклонена",
        reply_markup=ReplyKeyboardRemove(),
    )
