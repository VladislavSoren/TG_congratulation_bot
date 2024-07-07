from aiogram.fsm.state import StatesGroup, State


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
