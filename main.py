import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import (
    BotCommand,
)

from handlers import register_user_commands, bot_commands
from config import TG_BOT_TOKEN
from constants import TASK_INTERVAL_MINUTES
from dependencies import UserCheckMiddleware
from init_global_shedular import global_scheduler
from logger_global import logger
from mail import make_periodical_tasks, set_bot_instance

form_router = Router()


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
