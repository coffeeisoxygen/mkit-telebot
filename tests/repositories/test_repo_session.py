# ruff:noqa
# pyright: reportOptionalMemberAccess = false
from datetime import datetime

import pytest
from app.repositories.repo_session import SessionRepository


@pytest.mark.asyncio
async def test_create_and_get_by_id(db_session):
    repo = SessionRepository(db_session)
    obj_in = {
        "user_id": 1,
        "token": "token123",
        "ip_address": "127.0.0.1",
        "user_agent": "pytest",
        "last_activity": datetime.now(),
        "created_at": datetime.now(),
        "is_active": True,
    }
    new_session = await repo.create(obj_in)
    assert new_session.token == "token123"
    fetched = await repo.get_by_id(new_session.id)
    assert fetched.token == "token123"  # type: ignore


@pytest.mark.asyncio
async def test_get_by_token(db_session):
    repo = SessionRepository(db_session)
    obj_in = {
        "user_id": 2,
        "token": "token456",
        "ip_address": "127.0.0.2",
        "user_agent": "pytest",
        "last_activity": datetime.now(),
        "created_at": datetime.now(),
        "is_active": True,
    }
    new_session = await repo.create(obj_in)
    fetched = await repo.get_by_token("token456")
    assert fetched.user_id == 2  # type: ignore


@pytest.mark.asyncio
async def test_list_by_user(db_session):
    repo = SessionRepository(db_session)
    obj_in1 = {
        "user_id": 3,
        "token": "tokenA",
        "ip_address": "127.0.0.3",
        "user_agent": "pytest",
        "last_activity": datetime.now(),
        "created_at": datetime.now(),
        "is_active": True,
    }
    obj_in2 = {
        "user_id": 3,
        "token": "tokenB",
        "ip_address": "127.0.0.3",
        "user_agent": "pytest",
        "last_activity": datetime.now(),
        "created_at": datetime.now(),
        "is_active": True,
    }
    await repo.create(obj_in1)
    await repo.create(obj_in2)
    sessions = await repo.list_by_user(3)
    assert len(sessions) == 2


@pytest.mark.asyncio
async def test_update_activity(db_session):
    repo = SessionRepository(db_session)
    obj_in = {
        "user_id": 4,
        "token": "tokenX",
        "ip_address": "127.0.0.4",
        "user_agent": "pytest",
        "last_activity": datetime(2020, 1, 1),
        "created_at": datetime.now(),
        "is_active": True,
    }
    new_session = await repo.create(obj_in)
    updated = await repo.update_activity(new_session.id, datetime(2025, 9, 2))
    assert updated.last_activity == datetime(2025, 9, 2)  # pyright: ignore[reportOptionalMemberAccess]


@pytest.mark.asyncio
async def test_set_active(db_session):
    repo = SessionRepository(db_session)
    obj_in = {
        "user_id": 5,
        "token": "tokenY",
        "ip_address": "127.0.0.5",
        "user_agent": "pytest",
        "last_activity": datetime.now(),
        "created_at": datetime.now(),
        "is_active": True,
    }
    new_session = await repo.create(obj_in)
    deactivated = await repo.set_active(new_session.id, False)
    assert deactivated.is_active is False
    activated = await repo.set_active(new_session.id, True)
    assert activated.is_active is True


@pytest.mark.asyncio
async def test_delete(db_session):
    repo = SessionRepository(db_session)
    obj_in = {
        "user_id": 6,
        "token": "tokenZ",
        "ip_address": "127.0.0.6",
        "user_agent": "pytest",
        "last_activity": datetime.now(),
        "created_at": datetime.now(),
        "is_active": True,
    }
    new_session = await repo.create(obj_in)
    deleted = await repo.delete(new_session.id)
    assert deleted is True
    fetched = await repo.get_by_id(new_session.id)
    assert fetched is None
