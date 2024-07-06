__all__ = ['commands']

from aiogram import Router, F
from aiogram.filters import Command

from handlers.commands import command_start, cancel_handler

bot_commands = (
    ("start", "start command", "start command description"),
)


def register_user_commands(router: Router) -> None:
    router.message.register(command_start, Command("start"))
    router.message.register(cancel_handler, Command("cancel"))
    router.message.register(cancel_handler, F.text.casefold() == "отменить")
