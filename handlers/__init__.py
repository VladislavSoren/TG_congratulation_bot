__all__ = ['commands']

from aiogram import Router, F
from aiogram.filters import Command

from config import Form
from dependencies import UserCheckRequired
from handlers.auth import request_surname, request_name, request_otchestvo, request_birthday, check_info, \
    check_info_yes, check_info_no
from handlers.commands import command_start, cancel_handler

bot_commands = (
    ("start", "start command", "start command description"),
)


def register_user_commands(router: Router) -> None:
    # commands
    router.message.register(command_start, Command("start"))
    router.message.register(cancel_handler, Command("cancel"))
    router.message.register(cancel_handler, F.text.casefold() == "отменить")

    # auth
    router.message.register(request_surname, F.text.casefold() == "авторизоваться", UserCheckRequired())
    router.message.register(request_name, Form.surname)
    router.message.register(request_otchestvo, Form.name)
    router.message.register(request_birthday, Form.otchestvo)
    router.message.register(check_info, Form.birthday)
    router.message.register(check_info_yes, Form.check_info, F.text.casefold() == "да")
    router.message.register(check_info_no, Form.check_info, F.text.casefold() == "нет")
