from datetime import datetime

from sqlalchemy import text, exc, select, Result, true

from db.db_helper import db_helper
from db.models import User, Subscriber, UserSubscriber


async def create_user(user_info: dict):
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


async def get_user_by_telegram_id(obj_id: int):
    async with db_helper.async_session_factory() as session:
        obj = await session.get(User, obj_id)
        return obj


async def get_users_by_filters(
        surname=None,
        name=None,
        otchestvo=None,
):
    async with db_helper.async_session_factory() as session:
        filter_surname = User.surname == surname if surname else true()
        filter_name = User.name == name if name else true()
        filter_otchestvo = User.otchestvo == otchestvo if otchestvo else true()

        filters = filter_surname & filter_name & filter_otchestvo

        stmt = select(User).order_by(User.surname.asc()).filter(filters)
        result: Result = await session.execute(stmt)
        objs = result.scalars().all()

        return objs


async def create_subscriber(user_id: int):
    async with db_helper.async_session_factory() as session:

        await session.execute(text('pragma foreign_keys=on'))

        obj = Subscriber(
            user_id=user_id
        )
        session.add(obj)

        try:
            await session.commit()
        except exc.IntegrityError as e:
            await session.rollback()


async def subscribe_all(user_id: int):
    async with db_helper.async_session_factory() as session:

        await session.execute(text('pragma foreign_keys=on'))

        # Получаем id юзера как подписчика
        stmt = select(Subscriber).where(Subscriber.user_id == user_id)
        result: Result = await session.execute(stmt)
        subscriber_id = result.scalars().one().id

        # Получаем ВСЕХ юзеров кроме текущего
        stmt = select(User).where(User.id != user_id)
        result: Result = await session.execute(stmt)
        objs = result.scalars().all()

        # Создаем точку сохранения
        savepoint = await session.begin_nested()

        for obj_iter in objs:

            obj = UserSubscriber(
                user_id=obj_iter.id,
                subscriber_id=subscriber_id,
            )
            session.add(obj)

            try:
                await session.commit()
                savepoint = await session.begin_nested()
            except exc.IntegrityError as e:
                await savepoint.rollback()
                continue


async def subscribe_one_user(user_id: int, users: list[User]):
    async with db_helper.async_session_factory() as session:

        await session.execute(text('pragma foreign_keys=on'))

        # Получаем id юзера как подписчика
        stmt = select(Subscriber).where(Subscriber.user_id == user_id)
        result: Result = await session.execute(stmt)
        subscriber_id = result.scalars().one().id

        # Создаем точку сохранения
        savepoint = await session.begin_nested()

        for obj_iter in users:

            obj = UserSubscriber(
                user_id=obj_iter.id,
                subscriber_id=subscriber_id,
            )
            session.add(obj)

            try:
                await session.commit()
                savepoint = await session.begin_nested()
            except exc.IntegrityError as e:
                await savepoint.rollback()
                continue



