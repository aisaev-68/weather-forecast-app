from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import settings
from app.utils.logger import get_logger


logger = get_logger("models.database")

engine = create_async_engine(
    settings.DB_URI,
    echo=settings.POSTGRES_ECHO,
    future=True
)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс для моделей."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Генератор сессии для зависимостей FastAPI.

    :yield: AsyncSession
    """
    async with async_session() as session:
        logger.debug("Получена сессия. Pool: %s", engine.pool.status())
        yield session


async def init_db() -> None:
    """
    Инициализация базы данных — создание таблиц.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Таблицы созданы")
