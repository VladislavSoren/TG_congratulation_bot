from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    # флаг означающий, что таблица НЕ будет создаваться
    __abstract__ = True

    # имя таблицы создаётся на основе имени класса
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    # у всех сущностей будет колонка id
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
