from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.repositories.repo_user import UserRepository
from app.services.hasher.argonhasher import Argon2Hasher
from app.services.users.srv_user_crud import UserCrudService


def get_user_repository(
    db_session: AsyncSession = Depends(get_session),
) -> UserRepository:
    """Dependency untuk mendapatkan instance UserRepository.

    Args:
        db_session: Database session dari dependency injection.

    Returns:
        UserRepository: Instance repository user.
    """
    return UserRepository(db_session)


def get_password_hasher() -> Argon2Hasher:
    """Dependency untuk mendapatkan instance Argon2Hasher.

    Returns:
        Argon2Hasher: Instance hasher password.
    """
    return Argon2Hasher()


def get_user_service(
    repo: UserRepository = Depends(get_user_repository),
    hasher: Argon2Hasher = Depends(get_password_hasher),
) -> UserCrudService:
    """Dependency untuk mendapatkan instance UserCrudService.

    Args:
        repo: Repository user.
        hasher: Service hasher password.

    Returns:
        UserCrudService: Instance service user CRUD.
    """
    return UserCrudService(repo, hasher)
