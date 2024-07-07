from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


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
                KeyboardButton(text="Отписаться"),
            ]
        ],
        resize_keyboard=True,
    )


def auth_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Авторизоваться"),
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
