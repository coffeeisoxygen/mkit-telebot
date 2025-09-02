from datetime import datetime, timedelta

import pytest
from app.custom.exception.exceptions import EntityNotFoundError, SessionGenericError
from app.schemas import SessionInDB
from app.services.auth.srv_session import SessionService


@pytest.fixture
def mock_repo(mocker):
    repo = mocker.Mock()
    repo.create = mocker.AsyncMock()
    repo.get_by_token = mocker.AsyncMock()
    repo.update_activity = mocker.AsyncMock()
    repo.set_active = mocker.AsyncMock()
    repo.delete = mocker.AsyncMock()
    repo.list_by_user = mocker.AsyncMock()
    repo.list_active_sessions = mocker.AsyncMock()
    repo.get_by_id = mocker.AsyncMock()
    repo.session = mocker.Mock()
    repo.session.flush = mocker.AsyncMock()
    return repo


@pytest.fixture
def service(mock_repo):
    return SessionService(mock_repo)


@pytest.fixture
def session_data():
    return SessionInDB(
        id=1,
        user_id=1,
        token="token123",
        ip_address="127.0.0.1",
        user_agent="pytest",
        last_activity=datetime.now(),
        created_at=datetime.now(),
        is_active=True,
        expires_at=datetime.now() + timedelta(hours=1),
    )


@pytest.mark.asyncio
async def test_create_session_success(service, mock_repo, session_data):
    # Arrange
    mock_repo.create.return_value = session_data

    # Act
    result = await service.create_session(
        user_id=1,
        token="token123",
        ip_address="127.0.0.1",
        user_agent="pytest",
        expires_in=3600,
    )

    # Assert
    assert result == session_data
    mock_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_session_error(service, mock_repo, mocker):
    # Arrange
    mock_repo.create.side_effect = Exception("DB error")

    # Act & Assert
    with pytest.raises(SessionGenericError):
        await service.create_session(
            user_id=1,
            token="token123",
            ip_address="127.0.0.1",
            user_agent="pytest",
            expires_in=3600,
        )


@pytest.mark.asyncio
async def test_get_session_by_token_found(service, mock_repo, session_data):
    # Arrange
    mock_repo.get_by_token.return_value = session_data

    # Act
    result = await service.get_session_by_token("token123")

    # Assert
    assert result == session_data
    mock_repo.get_by_token.assert_called_once_with("token123")


@pytest.mark.asyncio
async def test_get_session_by_token_not_found(service, mock_repo):
    # Arrange
    mock_repo.get_by_token.return_value = None

    # Act & Assert
    with pytest.raises(EntityNotFoundError):
        await service.get_session_by_token("notfound")


@pytest.mark.asyncio
async def test_get_session_by_token_inactive(service, mock_repo, session_data):
    # Arrange
    session_data.is_active = False
    mock_repo.get_by_token.return_value = session_data

    # Act & Assert
    with pytest.raises(SessionGenericError):
        await service.get_session_by_token("token123")


@pytest.mark.asyncio
async def test_get_session_by_token_expired(service, mock_repo, session_data):
    # Arrange
    session_data.expires_at = datetime.now() - timedelta(seconds=1)
    mock_repo.get_by_token.return_value = session_data

    # Act & Assert
    with pytest.raises(SessionGenericError):
        await service.get_session_by_token("token123")


@pytest.mark.asyncio
async def test_refresh_activity_success(service, mock_repo, session_data):
    # Arrange
    mock_repo.update_activity.return_value = session_data

    # Act
    result = await service.refresh_activity(1)

    # Assert
    assert result == session_data
    mock_repo.update_activity.assert_called_once()


@pytest.mark.asyncio
async def test_refresh_activity_not_found(service, mock_repo):
    # Arrange
    mock_repo.update_activity.return_value = None

    # Act & Assert
    with pytest.raises(EntityNotFoundError):
        await service.refresh_activity(1)


@pytest.mark.asyncio
async def test_deactivate_session_success(service, mock_repo, session_data):
    # Arrange
    mock_repo.set_active.return_value = session_data

    # Act
    result = await service.deactivate_session(1)

    # Assert
    assert result == session_data
    mock_repo.set_active.assert_called_once_with(1, False)


@pytest.mark.asyncio
async def test_deactivate_session_not_found(service, mock_repo):
    # Arrange
    mock_repo.set_active.return_value = None

    # Act & Assert
    with pytest.raises(EntityNotFoundError):
        await service.deactivate_session(1)


@pytest.mark.asyncio
async def test_delete_session_success(service, mock_repo):
    # Arrange
    mock_repo.delete.return_value = True

    # Act
    result = await service.delete_session(1)

    # Assert
    assert result is True
    mock_repo.delete.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_delete_session_not_found(service, mock_repo):
    # Arrange
    mock_repo.delete.return_value = False

    # Act & Assert
    with pytest.raises(EntityNotFoundError):
        await service.delete_session(1)


@pytest.mark.asyncio
async def test_list_sessions_by_user(service, mock_repo, session_data):
    # Arrange
    mock_repo.list_by_user.return_value = [session_data]

    # Act
    result = await service.list_sessions_by_user(1)

    # Assert
    assert result == [session_data]
    mock_repo.list_by_user.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_list_active_sessions(service, mock_repo, session_data):
    # Arrange
    mock_repo.list_active_sessions.return_value = [session_data]

    # Act
    result = await service.list_active_sessions()

    # Assert
    assert result == [session_data]
    mock_repo.list_active_sessions.assert_called_once()


@pytest.mark.asyncio
async def test_update_expiry_success(service, mock_repo, session_data):
    # Arrange
    mock_repo.get_by_id.return_value = session_data
    mock_repo.session.flush.return_value = None

    # Act
    result = await service.update_expiry(1, 3600)

    # Assert
    assert result == session_data
    mock_repo.get_by_id.assert_called_once_with(1)
    mock_repo.session.flush.assert_called_once()


@pytest.mark.asyncio
async def test_update_expiry_not_found(service, mock_repo):
    # Arrange
    mock_repo.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(EntityNotFoundError):
        await service.update_expiry(1, 3600)


@pytest.mark.asyncio
async def test_reactivate_session_success(service, mock_repo, session_data):
    # Arrange
    mock_repo.set_active.return_value = session_data

    # Act
    result = await service.reactivate_session(1)

    # Assert
    assert result == session_data
    mock_repo.set_active.assert_called_once_with(1, True)


@pytest.mark.asyncio
async def test_reactivate_session_not_found(service, mock_repo):
    # Arrange
    mock_repo.set_active.return_value = None

    # Act & Assert
    with pytest.raises(EntityNotFoundError):
        await service.reactivate_session(1)
