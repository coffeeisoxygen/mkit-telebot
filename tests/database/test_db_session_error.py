import pytest
from app.custom.exception import InternalServiceError
from app.database.session import get_session, get_session_manual, sessionmanager
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_sessionmanager_connect_engine_none(monkeypatch, restore_sessionmanager):  # noqa: ARG001
    # Simulate engine None
    monkeypatch.setattr(sessionmanager, "engine", None)
    with pytest.raises(InternalServiceError):
        async with sessionmanager.connect():
            pass


@pytest.mark.asyncio
async def test_sessionmanager_session_sessionmaker_none(
    monkeypatch,
    restore_sessionmanager,  # noqa: ARG001
):
    # Simulate sessionmaker None
    monkeypatch.setattr(sessionmanager, "_sessionmaker", None)
    with pytest.raises(InternalServiceError):
        async with sessionmanager.session():
            pass


@pytest.mark.asyncio
async def test_get_session_dependency():
    # Simulate FastAPI dependency usage
    async def dummy():
        async for session in get_session():
            assert isinstance(session, AsyncSession)

    await dummy()


@pytest.mark.asyncio
async def test_get_session_manual_dependency():
    # Simulate FastAPI dependency usage
    async def dummy():
        async for session in get_session_manual():
            assert isinstance(session, AsyncSession)

    await dummy()
