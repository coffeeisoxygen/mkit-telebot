import pytest
from app.custom.exception.exceptions import UserDuplicateError
from app.repositories.repo_user import UserRepository
from app.schemas.sch_user import UserCreate, UserPublicResponse
from app.services.hasher.interface import IPasswordHasher
from app.services.users.srv_user_crud import UserCrudService
from sqlalchemy import text

pytestmark = pytest.mark.unit


class DummyHasher(IPasswordHasher):
    def hash_password(self, password: str) -> str:
        return f"hashed-{password}"

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed-{password}"


@pytest.fixture(scope="function", autouse=True)
async def clean_user_table(db_session):
    await db_session.execute(text("DELETE FROM users"))
    await db_session.commit()


@pytest.fixture
async def user_service(db_session):
    repo = UserRepository(db_session)
    hasher = DummyHasher()
    return UserCrudService(repo, hasher)


@pytest.fixture
def user_create_data():
    return UserCreate(username="testuser", full_name="Test User", password="secretpass")


@pytest.mark.asyncio
async def test_create_user_success(user_service, user_create_data):
    user = await user_service.create_user(user_create_data)
    assert user.username == user_create_data.username
    assert user.full_name == user_create_data.full_name
    assert user.hashed_password == "hashed-secretpass"
    assert isinstance(user, UserPublicResponse)


@pytest.mark.asyncio
async def test_create_user_duplicate(user_service, user_create_data):
    await user_service.create_user(user_create_data)
    with pytest.raises(UserDuplicateError):
        await user_service.create_user(user_create_data)


@pytest.mark.asyncio
async def test_create_user_password_is_hashed(user_service, user_create_data):
    user = await user_service.create_user(user_create_data)
    assert user.hashed_password.startswith("hashed-")
    assert user.hashed_password != user_create_data.password
    assert user_service.password_hasher.verify_password(
        user_create_data.password, user.hashed_password
    )
