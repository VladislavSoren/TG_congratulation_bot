from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.filters import BaseFilter
from aiogram.types import Message

from db.crud import get_user_by_telegram_id


async def check_user_exists(message: types.Message):
    user_db = await get_user_by_telegram_id(message.from_user.id)
    return user_db


class UserCheckRequired(BaseFilter):
    def __init__(self, required: bool = True):
        self.required = required

    async def __call__(self, message: Message) -> dict:
        return {'user_check': True}


class UserCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if data.get('user_check'):
            user_db = await check_user_exists(event)
            data['user_db'] = user_db
        return await handler(event, data)
