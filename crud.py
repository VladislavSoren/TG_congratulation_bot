from datetime import datetime

from sqlalchemy import text, exc

from db.db_helper import db_helper
from db.models import User


async def create_user(user_info):
    async with db_helper.async_session_factory() as session:

        await session.execute(text('pragma foreign_keys=on'))

        # Prepare data
        birthday = datetime.strptime(str(user_info["birthday"]), '%d.%m.%Y')

        obj = User(
            id=int(user_info["id_telegram"]),
            username_telegram=user_info["username_telegram"],
            surname=user_info["surname"],
            name=user_info["name"],
            otchestvo=user_info["otchestvo"],
            birthday=birthday,
        )
        session.add(obj)

        try:
            await session.commit()
        except exc.IntegrityError as e:
            await session.rollback()
            raise


async def get_user_by_telegram_id(obj_id):
    async with db_helper.async_session_factory() as session:
        obj = await session.get(User, obj_id)
        return obj
