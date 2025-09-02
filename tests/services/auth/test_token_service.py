import pytest
from app.services.auth.srv_token import TokenService
from app.schemas import TokenData

# ruff: noqa


@pytest.mark.asyncio
async def test_create_token_and_decode_token():
    # Arrange
    service = TokenService()
    user_id = 123
    username = "testuser"
    scopes = ["admin", "user"]

    # Act
    token_response = await service.create_token(user_id, username, scopes)
    decoded = await service.decode_token(token_response.access_token)

    # Assert
    assert token_response.access_token
    assert token_response.expires_in > 0
    assert decoded is not None
    assert decoded.user_id == user_id
    assert decoded.username == username
    assert set(decoded.scopes) == set(scopes)


@pytest.mark.asyncio
async def test_decode_token_invalid():
    # Arrange
    service = TokenService()
    invalid_token = "invalid.token.value"

    # Act
    result = await service.decode_token(invalid_token)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_is_scope_allowed_true_false():
    # Arrange
    service = TokenService()
    token_data = TokenData(user_id=1, username="u", scopes=["admin", "user"])

    # Act & Assert
    assert await service.is_scope_allowed(token_data, "admin") is True
    assert await service.is_scope_allowed(token_data, "user") is True
    assert await service.is_scope_allowed(token_data, "other") is False


@pytest.mark.asyncio
async def test_create_token_default_scope():
    # Arrange
    service = TokenService()
    user_id = 1
    username = "defaultscope"

    # Act
    token_response = await service.create_token(user_id, username)
    decoded = await service.decode_token(token_response.access_token)

    # Assert
    assert decoded is not None
    assert decoded.scopes == ["user"]
