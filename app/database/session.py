r"""Database Session Management Module.

This module provides async database session and connection management using SQLAlchemy 2.0 style.
It supports multiple context manager patterns for transaction control, including manual commit,
automatic commit, and recommended Unit of Work (UoW) pattern.

USAGE GUIDELINES:

1. get_db_transaction() - RECOMMENDED for most cases
   - Simple CRUD operations
   - Business logic that should be atomic
   - Automatic UoW pattern with SQLAlchemy v2

2. get_db_session_manual_commit() - For complex scenarios
   - Multi-step operations with conditional commits
   - External API integrations
   - Need fine-grained transaction control

3. get_db_session_auto_commit() - For simple operations
   - Single operation that should always commit
   - Less sophisticated than UoW pattern

Examples:
# Simple operation (RECOMMENDED)
async def create_user(user_data: UserCreate) -> User:
    async with get_db_transaction() as session:
        return await UserCRUD.create(session, user_data)

# Complex operation
async def complex_order_process(order_data: OrderCreate) -> OrderResult:
    async with get_db_session_manual_commit() as session:
        try:
            # Step 1
            order = await OrderCRUD.create(session, order_data)
            await session.commit()  # Intermediate commit

            # Step 2: External API
            payment = await payment_service.charge(order.total)

            if payment.success:
                order.status = "paid"
                await session.commit()
            else:
                await session.rollback()

        except Exception:
            await session.rollback()
            raise
"""

import contextlib
from collections.abc import AsyncIterator

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings
from app.custom.exception import InternalServiceError

settings = get_settings()


class DatabaseSessionManager:
    """Manages async database connections and sessions.

    This class provides methods to create and manage database sessions
    using SQLAlchemy's async capabilities. It ensures proper handling of
    transactions and connections.
    """

    def __init__(self, db_url: str):
        # Only pass pool_size and max_overflow if not SQLite
        engine_kwargs = {
            "url": db_url,
            "echo": settings.DB.echo,
            "connect_args": {"timeout": settings.DB.timeout},
        }
        if not db_url.startswith("sqlite"):  # covers sqlite+aiosqlite, sqlite://, etc
            engine_kwargs["pool_size"] = settings.DB.pool_size
            engine_kwargs["max_overflow"] = settings.DB.max_overflow
        self.engine: AsyncEngine | None = create_async_engine(**engine_kwargs)
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = (
            async_sessionmaker(bind=self.engine, expire_on_commit=False)
        )
        logger.debug("DatabaseSessionManager initialized")

    async def close(self) -> None:
        """Dispose engine and reset sessionmaker.

        This method is responsible for cleaning up the database engine
        and sessionmaker resources when they are no longer needed.
        """
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self._sessionmaker = None
            logger.debug("Database engine disposed")

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        """Provide an async connection (non-ORM).

        This method creates a new database connection and yields it to the caller.
        It ensures proper error handling and connection management.

        Raises:
            InternalServiceError: If the database engine is not initialized
            InternalServiceError: If an error occurs while connecting
            InternalServiceError: If an error occurs while yielding the connection

        Returns:
            AsyncIterator[AsyncConnection]: An async iterator over the database connection.

        Yields:
            Iterator[AsyncIterator[AsyncConnection]]: An async iterator over the database connection.
        """
        if self.engine is None:
            raise InternalServiceError("Database engine is not initialized")

        try:
            async with self.engine.connect() as connection:
                try:
                    yield connection
                except SQLAlchemyError as e:
                    await connection.rollback()
                    logger.bind(
                        method="connect", db_url=str(self.engine.url)
                    ).exception("Connection error occurred")
                    raise InternalServiceError(message=str(e), cause=e) from e
        except SQLAlchemyError as e:
            # Catch error from __aenter__ (e.g. connection failure)
            logger.bind(method="connect", db_url=str(self.engine.url)).exception(
                "Connection error occurred on __aenter__"
            )
            raise InternalServiceError(message=str(e), cause=e) from e

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Provide an async session with rollback and close handling.

        This method provides an async session with rollback and close handling.

        Raises:
            InternalServiceError: If the sessionmaker is not available
            InternalServiceError: If an error occurs while creating the session
            InternalServiceError: If an error occurs while yielding the session

        Returns:
            AsyncIterator[AsyncSession]: An async iterator over the database session.

        Yields:
            Iterator[AsyncIterator[AsyncSession]]: An async iterator over the database session.
        """
        if not self._sessionmaker:
            logger.error("Sessionmaker is not available")
            raise InternalServiceError("Sessionmaker is not available")

        async with self._sessionmaker() as session:
            try:
                yield session
            except SQLAlchemyError as e:
                await session.rollback()
                db_url = str(self.engine.url) if self.engine else "N/A"
                logger.bind(method="session", db_url=db_url).exception("Session error")
                raise InternalServiceError(message=str(e), cause=e) from e
            except Exception as e:
                await session.rollback()
                db_url = str(self.engine.url) if self.engine else "N/A"
                logger.bind(method="session", db_url=db_url).exception(
                    "Unexpected session error"
                )
                raise InternalServiceError(message=str(e), cause=e) from e
            finally:
                await session.close()


# Singleton instance for FastAPI
sessionmanager = DatabaseSessionManager(settings.DB.url)


@contextlib.asynccontextmanager
async def get_db_session_manual_commit() -> AsyncIterator[AsyncSession]:
    """Database session with manual commit control.

    Use for complex operations that need fine-grained transaction control.
    Caller must commit/rollback explicitly.

    Example:
        async with get_db_session_manual_commit() as session:
            user = await UserCRUD.create(session, user_data)
            await session.commit()  # Manual commit
    """
    async with sessionmanager.session() as session:
        yield session


@contextlib.asynccontextmanager
async def get_db_session_auto_commit() -> AsyncIterator[AsyncSession]:
    """Database session with automatic commit.

    Use for simple operations that should always commit on success.
    Automatically commits if no exception occurs, rollbacks on error.

    Example:
        async with get_db_session_auto_commit() as session:
            user = await UserCRUD.create(session, user_data)
            # Auto commit here
    """
    async with sessionmanager.session() as session:
        try:
            yield session
            await session.commit()  # Auto commit if no exception
        except Exception as e:
            await session.rollback()  # Auto rollback on error
            logger.bind(method="auto_commit_session").exception(
                "Auto commit session error"
            )
            raise InternalServiceError(message=str(e), cause=e) from e


@contextlib.asynccontextmanager
async def get_db_transaction() -> AsyncIterator[AsyncSession]:
    """Database session with SQLAlchemy UoW pattern (RECOMMENDED).

    Uses SQLAlchemy's built-in Unit of Work pattern with session.begin().
    Automatically commits on success, rollbacks on exception.
    This is the recommended approach for most operations.

    Example:
        async with get_db_transaction() as session:
            user = await UserCRUD.create(session, user_data)
            product.stock -= 1  # Tracked automatically
            # Auto commit/rollback handled by session.begin()
    """
    async with sessionmanager.session() as session, session.begin():
        try:
            yield session
            # Auto commit handled by session.begin() context manager
        except SQLAlchemyError as e:
            db_url = str(sessionmanager.engine.url) if sessionmanager.engine else "N/A"
            logger.bind(method="transaction", db_url=db_url).exception(
                "Transaction error"
            )
            # Auto rollback handled by session.begin() context manager
            raise InternalServiceError(message=str(e), cause=e) from e
        except Exception as e:
            db_url = str(sessionmanager.engine.url) if sessionmanager.engine else "N/A"
            logger.bind(method="transaction", db_url=db_url).exception(
                "Unexpected transaction error"
            )
            # Auto rollback handled by session.begin() context manager
            raise InternalServiceError(message=str(e), cause=e) from e


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency for database session (uses recommended UoW pattern).

    Usage in controllers:
        @router.get("/users")
        async def get_users(session: AsyncSession = Depends(get_session)):
            # Use session directly
    """
    async with get_db_transaction() as session:
        yield session


async def get_session_manual() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency for manual commit control.

    Usage in controllers that need explicit commit control:
        @router.post("/complex-operation")
        async def complex_op(session: AsyncSession = Depends(get_session_manual)):
            # Manual commit control
            await session.commit()
    """
    async with get_db_session_manual_commit() as session:
        yield session
