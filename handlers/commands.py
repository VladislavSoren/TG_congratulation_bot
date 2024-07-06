from contextlib import suppress
from typing import Any

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from constants import START_MESSAGE, CANCEL_MESSAGE
from keyboards import main_menu
from logger_global import logger


async def command_start(message: Message) -> Message:
    return await message.answer(
        START_MESSAGE,
        reply_markup=main_menu()
    )


async def cancel_handler(message: Message, state: FSMContext) -> Any:
    """
    Позволяет юзеру отменить некое действие
    """
    await message.delete()

    current_state = await state.get_state()

    logger.info("Cancelling state %r", current_state)
    await state.clear()
    with suppress(Exception):
        await message.delete()

    return await message.answer(
        CANCEL_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    )
