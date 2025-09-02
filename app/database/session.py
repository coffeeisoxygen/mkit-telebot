import contextlib
from collections.abc import AsyncIterator

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.custom.exception import DataBaseServiceError

settings = get_settings()


class DatabaseSessionManager:
    """Manages async database connections and sessions."""

    def __init__(self, db_url: str):
        self.engine = create_async_engine(
            url=db_url,
            echo=settings.DB.echo,
            connect_args={"timeout": settings.DB.timeout},
            # Conditionally set pool args for non-SQLite
            pool_size=settings.DB.pool_size
            if not db_url.startswith("sqlite")
            else None,
            max_overflow=settings.DB.max_overflow
            if not db_url.startswith("sqlite")
            else None,
        )
        self._sessionmaker = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )
        logger.debug("DatabaseSessionManager initialized")

    async def close(self) -> None:
        """Dispose engine and reset sessionmaker."""
        if self.engine:
            await self.engine.dispose()
            logger.debug("Database engine disposed")

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            logger.exception("Sessionmaker is not available")
            raise DataBaseServiceError(
                message="Sessionmaker is not available", context={}
            )

        async with self._sessionmaker() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()  # rollback kalau error
                logger.error(f"DB session rollback karena error: {e}")
                raise
            finally:
                await session.close()


# Singleton instance
sessionmanager = DatabaseSessionManager(settings.DB.url)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency for a single database session."""
    async with sessionmanager.session() as session:
        yield session
