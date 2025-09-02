from unittest.mock import AsyncMock, MagicMock

import pytest
from app.services.users.srv_seed_admin import seed_default_admin
from sqlalchemy.exc import IntegrityError


@pytest.mark.asyncio
async def test_seed_default_admin_success():
    # Arrange
    repo = MagicMock()
    repo.get_active_superuser = AsyncMock(return_value=None)
    repo.create = AsyncMock()
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
    repo.get_active_superuser.assert_awaited_once()
    repo.create.assert_awaited_once()
    repo.session.commit.assert_awaited_once()
    assert result is True


@pytest.mark.asyncio
async def test_seed_default_admin_already_exists():
    # Arrange
    repo = MagicMock()
    repo.get_active_superuser = AsyncMock(return_value={"id": 1})
    hasher = MagicMock()
    config = MagicMock()

    # Act
    result = await seed_default_admin(repo, hasher, config)

    # Assert
    repo.get_active_superuser.assert_awaited_once()
    assert result is False


@pytest.mark.asyncio
async def test_seed_default_admin_integrity_error():
    # Arrange
    repo = MagicMock()
    repo.get_active_superuser = AsyncMock(return_value=None)
    repo.create = AsyncMock(side_effect=IntegrityError("err", "params", "orig"))
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
