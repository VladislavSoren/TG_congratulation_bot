from datetime import datetime, timedelta

from aiogram import Bot

from constants import BIRTHDAY_DATE_FORMAT, FULL_DATE_FORMAT
from crud import get_users_by_filters, get_all_users_subscribers_ids_set, get_user_by_telegram_id
from init_global_shedular import global_scheduler

bot_instance: Bot = None


def set_bot_instance(bot: Bot):
    global bot_instance
    bot_instance = bot


async def send_message_to_user(user_id: int, text: str):
    await bot_instance.send_message(chat_id=user_id, text=text)


async def make_periodical_tasks():
    current_time = datetime.now()
    task_execute_date = current_time + timedelta(minutes=0)

    # Получаем юзеров с ДР == Текущая дата
    birthday = task_execute_date.strftime(BIRTHDAY_DATE_FORMAT)
    objs = await get_users_by_filters(birthday=birthday, birthday_filter_mon_day=True)

    # Создаём для рассылки по каждому юзеру задачу
    # Время выполнения делаем с небольшим сдвигом во избежание перегрузки
    for i, user in enumerate(objs):
        # Выставление стандартного времени
        task_execute_date = current_time + timedelta(seconds=i)

        global_scheduler.add_job(
            send_birthday_reminder,
            args=[int(user.id)],
            trigger="date",
            run_date=task_execute_date.strftime(FULL_DATE_FORMAT),
            misfire_grace_time=60,  # sec
        )
    global_scheduler.print_jobs()


async def send_birthday_reminder(user_id):

    # Получаем данные о юзере на которого подписаны
    user = await get_user_by_telegram_id(int(user_id))
    text_mess = f'Сегодня у {user.surname} {user.name} {user.otchestvo} ДР!'

    # Получаем всех подписчиков юзера из БД
    ids_set = await get_all_users_subscribers_ids_set(user_id)

    # Рассылаем напоминание всем, кроме себя
    for obj_id in ids_set:
        if int(user_id) != int(obj_id):
            await bot_instance.send_message(chat_id=obj_id, text=text_mess)

