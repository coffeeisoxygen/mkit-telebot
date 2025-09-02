from unittest.mock import AsyncMock, MagicMock

import pytest
from app.services.users.srv_seed_admin import seed_default_admin
from sqlalchemy.exc import IntegrityError


@pytest.mark.asyncio
async def test_seed_default_admin_success():
    # Arrange
    repo = MagicMock()
    repo.get_active_superuser = AsyncMock(return_value=None)
    repo.get_by_username = AsyncMock(return_value=None)
    repo.create = AsyncMock()

    class DummySession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        def begin(self):
            return self

    repo.session = DummySession()
    hasher = MagicMock()
    hasher.hash_password = AsyncMock(return_value="hashed_pw")
    config = MagicMock()
    config.username = "admin"
    config.full_name = "Admin"
    config.password = "password"
    config.is_active = True
    config.is_superuser = True

    # Act
    result = await seed_default_admin(repo, hasher, config)

    # Assert
    repo.get_active_superuser.assert_awaited_once()
    repo.get_by_username.assert_awaited_once()
    repo.create.assert_awaited_once()
    assert result is True


@pytest.mark.asyncio
async def test_seed_default_admin_already_exists():
    repo = MagicMock()
    repo.get_active_superuser = AsyncMock(return_value={"id": 1})
    repo.get_by_username = AsyncMock()

    class DummySession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        def begin(self):
            return self

    repo.session = DummySession()
    hasher = MagicMock()
    hasher.hash_password = AsyncMock(return_value="hashed_pw")
    config = MagicMock()
    config.username = "admin"
    config.full_name = "Admin"
    config.password = "password"
    config.is_active = True
    config.is_superuser = True

    result = await seed_default_admin(repo, hasher, config)

    repo.get_active_superuser.assert_awaited_once()
    repo.get_by_username.assert_not_called()
    assert result is False


@pytest.mark.asyncio
async def test_seed_default_admin_integrity_error():
    repo = MagicMock()
    repo.get_active_superuser = AsyncMock(return_value=None)
    repo.get_by_username = AsyncMock(return_value=None)
    repo.create = AsyncMock(side_effect=IntegrityError("err", "params", "orig"))  # type: ignore

    class DummySession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        def begin(self):
            return self

        async def rollback(self):
            pass

    repo.session = DummySession()
    hasher = MagicMock()
    hasher.hash_password = AsyncMock(return_value="hashed_pw")
    config = MagicMock()
    config.username = "admin"
    config.full_name = "Admin"
    config.password = "password"
    config.is_active = True
    config.is_superuser = True

    try:
        result = await seed_default_admin(repo, hasher, config)
    except IntegrityError:
        result = False

    repo.get_active_superuser.assert_awaited_once()
    repo.get_by_username.assert_awaited_once()
    repo.create.assert_awaited_once()
    assert result is False


@pytest.mark.asyncio
async def test_seed_default_admin_other_exception():
    # Arrange
    repo = MagicMock()
    repo.get_active_superuser = AsyncMock(return_value=None)
    repo.create = AsyncMock(side_effect=Exception("unexpected"))
    repo.session = AsyncMock()
    hasher = MagicMock()
    hasher.hash_password.return_value = "hashed_pw"
    config = MagicMock()
    config.username = "admin"
    config.full_name = "Admin"
    config.password = "password"
    config.is_active = True
    config.is_superuser = True

    # Act
    result = await seed_default_admin(repo, hasher, config)

    # Assert
    repo.session.rollback.assert_awaited_once()
    assert result is False


@pytest.mark.asyncio
async def test_seed_default_admin_username_taken():
    repo = MagicMock()
    repo.get_active_superuser = AsyncMock(return_value=None)
    repo.get_by_username = AsyncMock(return_value={"id": 2})
    repo.create = AsyncMock()

    class DummySession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        def begin(self):
            return self

    repo.session = DummySession()
    hasher = MagicMock()
    hasher.hash_password = AsyncMock(return_value="hashed_pw")
    config = MagicMock()
    config.username = "admin"
    config.full_name = "Admin"
    config.password = "password"
    config.is_active = True
    config.is_superuser = True

    result = await seed_default_admin(repo, hasher, config)

    repo.get_active_superuser.assert_awaited_once()
    repo.get_by_username.assert_awaited_once()
    repo.create.assert_not_called()
    assert result is False
