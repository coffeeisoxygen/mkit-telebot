import pytest
from app.custom.exception.exceptions import UserDuplicateError
from app.database.session import get_db_session_manual_commit
from app.repositories.repo_user import UserRepository
from app.services.users.schemas import UserCreate
from app.services.users.srv_user_crud import UserService

pytestmark = pytest.mark.unit


class DummyHasher:
    def hash_password(self, password: str) -> str:
        return f"hashed-{password}"


@pytest.fixture
async def user_service():
    async with get_db_session_manual_commit() as session:
        repo = UserRepository(session)
        hasher = DummyHasher()
        yield UserService(repo, hasher)  # type: ignore


@pytest.fixture
def user_create_data():
    return UserCreate(username="testuser", full_name="Test User", password="secretpass")


@pytest.fixture(autouse=True)
async def clean_user_table(db_session):
    from sqlalchemy import text

    await db_session.execute(text("DELETE FROM users"))
    await db_session.commit()


@pytest.mark.asyncio
async def test_create_user_success(user_service, user_create_data):
    user = await user_service.create_user(user_create_data)
    assert user.username == user_create_data.username
    assert user.hashed_password == "hashed-secretpass"
    assert user.full_name == user_create_data.full_name


@pytest.mark.asyncio
async def test_create_user_duplicate(user_create_data):
    async with get_db_session_manual_commit() as session:
        repo = UserRepository(session)
        hasher = DummyHasher()
        service = UserService(repo, hasher)  # type: ignore
        await service.create_user(user_create_data)
        await session.commit()
        # Duplikat: error baru muncul saat commit
        await service.create_user(user_create_data)
        with pytest.raises(UserDuplicateError):
            await session.commit()


@pytest.mark.asyncio
async def test_create_user_password_is_hashed(user_service, user_create_data):
    user = await user_service.create_user(user_create_data)
    assert user.hashed_password.startswith("hashed-")
    assert user.hashed_password != user_create_data.password
