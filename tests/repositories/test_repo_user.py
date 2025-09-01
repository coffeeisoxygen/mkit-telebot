import pytest
from app.custom.exception.exceptions import UserNotFoundError
from app.repositories.repo_user import UserRepository
from sqlalchemy import text

pytestmark = pytest.mark.unit


@pytest.fixture
async def repo(db_session):  # noqa: RUF029
    return UserRepository(db_session)


@pytest.fixture(autouse=True)
async def clean_user_table(db_session):
    # Bersihkan tabel user sebelum setiap test
    await db_session.execute(text("DELETE FROM users"))
    await db_session.commit()


@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "full_name": "Test User",
        "hashed_password": "hashedpass",
        "is_active": True,
        "is_superuser": False,
    }


@pytest.mark.asyncio
async def test_create_and_get_by_id(repo, user_data):
    # Arrange
    user = await repo.create(user_data)
    await repo.session.commit()
    # Act
    found = await repo.get_by_id(user.id)
    # Assert
    assert found is not None
    assert found.username == user_data["username"]


@pytest.mark.asyncio
async def test_get_by_username(repo, user_data):
    user = await repo.create(user_data)  # noqa: F841
    await repo.session.commit()
    found = await repo.get_by_username(user_data["username"])
    assert found is not None
    assert found.full_name == user_data["full_name"]


@pytest.mark.asyncio
async def test_update_user(repo, user_data):
    user = await repo.create(user_data)
    await repo.session.commit()
    updated = await repo.update(user.id, {"full_name": "Updated Name"})
    await repo.session.commit()
    assert updated.full_name == "Updated Name"


@pytest.mark.asyncio
async def test_delete_user(repo, user_data):
    user = await repo.create(user_data)
    await repo.session.commit()
    result = await repo.delete(user.id)
    await repo.session.commit()
    assert result is True
    with pytest.raises(UserNotFoundError):
        await repo.delete(user.id)


@pytest.mark.asyncio
async def test_list_and_filter_active(repo, user_data):
    user1 = await repo.create(user_data)
    user2 = await repo.create({**user_data, "username": "inactive", "is_active": False})
    await repo.session.commit()
    all_users = await repo.list()
    active_users = await repo.list(is_active=True)
    inactive_users = await repo.list(is_active=False)
    assert len(all_users) == 2
    assert len(active_users) == 1
    assert active_users[0].username == user1.username
    assert len(inactive_users) == 1
    assert inactive_users[0].username == user2.username


@pytest.mark.asyncio
async def test_update_not_found(repo):
    with pytest.raises(UserNotFoundError):
        await repo.update(9999, {"full_name": "Should Fail"})


@pytest.mark.asyncio
async def test_delete_not_found(repo):
    with pytest.raises(UserNotFoundError):
        await repo.delete(9999)
