from sqlalchemy.ext.asyncio import (

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


db_helper = DatabaseHelper(
    url=DB_URL,
    echo=DB_ECHO,
)
