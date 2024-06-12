from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from config import DB_URL, DB_ECHO


class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.async_session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    # def get_scoped_session(self):
    #     async_session = async_scoped_session(
    #         session_factory=self.async_session_factory,
    #         scopefunc=current_task,
    #     )
    #     return async_session
    #
    # # Создание сессии каждый раз (при новом обращении в view -> новая сессия)
    # async def session_dependency(self) -> AsyncSession:
    #     async with self.async_session_factory() as session:
    #         yield session
    #         await session.close()
    #
    # # одна сессия на view
    # async def scoped_session_dependency(self) -> AsyncSession:
    #     session = self.get_scoped_session()
    #     yield session
    #     await session.close()


db_helper = DatabaseHelper(
    url=DB_URL,
    echo=DB_ECHO,
)
