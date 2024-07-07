__all__ = ['commands']

from aiogram import Router, F
from aiogram.filters import Command

from utils.fsm_groups import Form
from utils.dependencies import UserCheckRequired
from handlers.auth import request_surname, request_name, request_otchestvo, request_birthday, check_info, \
    check_info_yes, check_info_no
from handlers.commands import command_start, cancel_handler
from handlers.subscribe import unsubscribe_all, subscribe_start, subscribe_all_users, request_surname_subscribe, \
    request_name_subscribe, request_otchestvo_subscribe, subscribe_request, subscribe_finish_ok, subscribe_finish_no

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

    # subscribe
    router.message.register(unsubscribe_all, F.text.casefold() == "отписаться", UserCheckRequired())
    router.message.register(subscribe_start, F.text.casefold() == "подписаться", UserCheckRequired())
    router.message.register(subscribe_all_users, F.text.casefold() == "на всех")
    router.message.register(request_surname_subscribe, F.text.casefold() == "на конкретного пользователя")
    router.message.register(request_name_subscribe, Form.surname_subscribe)

    router.message.register(request_otchestvo_subscribe, Form.name_subscribe)
    router.message.register(subscribe_request, Form.otchestvo_subscribe)
    router.message.register(subscribe_finish_ok, Form.subscribe_finish, F.text.casefold() == "да")
    router.message.register(subscribe_finish_no, Form.subscribe_finish, F.text.casefold() == "нет")
