import pytest
from app.services.hasher.argonhasher import Argon2Hasher


@pytest.fixture
def hasher():
    return Argon2Hasher()


def test_hash_password_returns_different_hash_for_same_password(hasher):
    # Arrange
    password = "password123"
    # Act
    hash1 = hasher.hash_password(password)
    hash2 = hasher.hash_password(password)
    # Assert
    assert hash1 != hash2
    assert hash1.startswith("$argon2id$")
    assert hash2.startswith("$argon2id$")


def test_verify_password_success(hasher):
    # Arrange
    password = "securepassword"
    hashed = hasher.hash_password(password)
    # Act
    result = hasher.verify_password(password, hashed)
    # Assert
    assert result is True


def test_verify_password_failure(hasher):
    # Arrange
    password = "securepassword"
    wrong_password = "wrongpassword"
    hashed = hasher.hash_password(password)
    # Act
    result = hasher.verify_password(wrong_password, hashed)
    # Assert
    assert result is False
