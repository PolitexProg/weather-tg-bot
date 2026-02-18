from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# URL для SQLite в асинхронном режиме
DATABASE_URL = "sqlite+aiosqlite:///./db.sqlite3"

# Создаем движок
engine = create_async_engine(DATABASE_URL, echo=True)

# Фабрика сессий
async_session = async_sessionmaker(engine, expire_on_commit=False)

# Базовый класс для моделей
class Base(DeclarativeBase):
    pass

# Пример модели пользователя

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(unique=True)
    username: Mapped[str | None] = mapped_column(nullable=True)
    city: Mapped[str | None] = mapped_column(nullable=True)
    age: Mapped[int | None] = mapped_column(nullable=True)
    hobbies: Mapped[str | None] = mapped_column(nullable=True)



# Функция для создания таблиц (вызывать при старте бота)
async def proceed_schemas():
    """Create database tables defined on the SQLAlchemy `Base` metadata.

    This function is intended to be called at application startup to ensure
    that the SQLite schema exists before the bot starts handling requests.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
