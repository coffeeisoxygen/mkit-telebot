import pytest
from app.custom.exception import InternalServiceError
from app.database.session import (
    get_db_session_auto_commit,
    get_db_transaction,
    sessionmanager,
)
from app.models.db_user import User
from sqlalchemy import select


@pytest.mark.asyncio
async def test_manual_commit_and_rollback(db_session):
    # Manual commit
    new_user = User(
        username="manualuser",
        full_name="Manual Commit",
        hashed_password="pw",
        is_active=True,
        is_superuser=False,
    )
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)
    assert new_user.id is not None

    # Manual rollback
    db_session.add(
        User(
            username="rollbackuser",
            full_name="Rollback",
            hashed_password="pw",
            is_active=True,
            is_superuser=False,
        )
    )
    await db_session.rollback()
    result = await db_session.execute(
        select(User).where(User.username == "rollbackuser")
    )
    assert result.scalar() is None

    # Cleanup
    await db_session.delete(new_user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_auto_commit_success_and_error():
    async with get_db_session_auto_commit() as session:
        user = User(
            username="autocommit",
            full_name="Auto Commit",
            hashed_password="pw",
            is_active=True,
            is_superuser=False,
        )
        session.add(user)
    # Confirm commit
    async with get_db_transaction() as session:
        result = await session.execute(
            select(User).where(User.username == "autocommit")
        )
        user_obj = result.scalar_one()
        assert user_obj.full_name == "Auto Commit"
        await session.delete(user_obj)
        await session.commit()

    # Error triggers rollback
    try:
        async with get_db_session_auto_commit() as session:
            session.add(
                User(
                    username=None,
                    full_name="Error",
                    hashed_password="pw",
                    is_active=True,
                    is_superuser=False,
                )
            )
    except InternalServiceError:
        pass
    # Confirm not inserted
    async with get_db_transaction() as session:
        result = await session.execute(select(User).where(User.full_name == "Error"))
        assert result.scalar() is None


@pytest.mark.asyncio
async def test_transaction_commit_and_rollback():
    # Commit
    async with get_db_transaction() as session:
        user = User(
            username="transuser",
            full_name="Trans Commit",
            hashed_password="pw",
            is_active=True,
            is_superuser=False,
        )
        session.add(user)
    async with get_db_transaction() as session:
        result = await session.execute(select(User).where(User.username == "transuser"))
        user_obj = result.scalar_one()
        assert user_obj.full_name == "Trans Commit"
        await session.delete(user_obj)
        await session.commit()

    # Rollback
    try:
        async with get_db_transaction() as session:
            session.add(
                User(
                    username=None,
                    full_name="Trans Error",
                    hashed_password="pw",
                    is_active=True,
                    is_superuser=False,
                )
            )
    except InternalServiceError:
        pass
    async with get_db_transaction() as session:
        result = await session.execute(
            select(User).where(User.full_name == "Trans Error")
        )
        assert result.scalar() is None


@pytest.mark.asyncio
async def test_sessionmanager_connect_and_close():
    # Test connect
    async with sessionmanager.connect() as conn:
        assert conn is not None
    # Test close
    await sessionmanager.close()
    assert sessionmanager.engine is None
    assert sessionmanager._sessionmaker is None
    # Re-init for other tests
    sessionmanager.__init__(
        sessionmanager.engine.url
        if sessionmanager.engine
        else "sqlite+aiosqlite:///telebot.db"
    )
