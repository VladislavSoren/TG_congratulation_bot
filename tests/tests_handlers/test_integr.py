import pytest
from aiogram import Dispatcher, Bot
from aiogram.methods import SendMessage

from utils.constants import START_MESSAGE
from utils.keyboards import main_menu
from tests.utils import get_update, get_message


@pytest.mark.asyncio
async def test_start_command(dispatcher: Dispatcher, bot: Bot):
    result: SendMessage = await dispatcher.feed_update(bot=bot, update=get_update(message=get_message(text='/start')))
    assert isinstance(result, SendMessage)
    assert result.text == START_MESSAGE
    assert result.reply_markup == main_menu()
