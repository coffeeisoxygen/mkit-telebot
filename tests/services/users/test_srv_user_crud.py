import pytest
from app.custom.exception.exceptions import UserDuplicateError
from app.models import User as Db_User
from app.repositories.repo_user import UserRepository
from app.schemas.sch_user import UserCreate, UserPublicResponse
from app.services.hasher.interface import IPasswordHasher
from app.services.users.srv_user_crud import UserCrudService
from sqlalchemy import select

pytestmark = pytest.mark.unit


class DummyHasher(IPasswordHasher):
    def hash_password(self, password: str) -> str:
        return f"hashed-{password}"

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed-{password}"


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
    # assert user.hashed_password == "hashed-secretpass"
    assert isinstance(user, UserPublicResponse)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username",
    ["testuser", "anotheruser", "dupeuser"],
)
async def test_create_user_duplicate(user_service, username):
    user_data = UserCreate(
        username=username, full_name="Test User", password="secretpass"
    )
    user1 = await user_service.create_user(user_data)
    assert user1.username == username
    # Pastikan duplikasi benar-benar raise error
    with pytest.raises(UserDuplicateError):
        await user_service.create_user(user_data)


@pytest.mark.asyncio
async def test_create_user_password_is_hashed(
    user_service: UserCrudService, user_create_data, db_session
):
    # Arrange
    await user_service.create_user(user_create_data)
    # Ambil user dari database

    stmt = select(Db_User).where(Db_User.username == user_create_data.username)
    result = await db_session.execute(stmt)
    db_user = result.scalar_one()
    # Assert
    assert db_user.hashed_password.startswith("hashed-")
    assert db_user.hashed_password != user_create_data.password
    assert user_service.password_hasher.verify_password(
        user_create_data.password, db_user.hashed_password
    )
