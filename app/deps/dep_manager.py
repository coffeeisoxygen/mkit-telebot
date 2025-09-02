from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.repositories.repo_session import SessionRepository
from app.repositories.repo_user import UserRepository
from app.services.auth.srv_auth import AuthService
from app.services.auth.srv_session import SessionService
from app.services.auth.srv_token import TokenService
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


# Dependency untuk SessionRepository dan SessionService
def get_session_repository(
    db_session: AsyncSession = Depends(get_session),
) -> SessionRepository:
    return SessionRepository(db_session)


def get_session_service(
    repo: SessionRepository = Depends(get_session_repository),
) -> SessionService:
    return SessionService(repo)


# Dependency untuk TokenService
def get_token_service() -> TokenService:
    return TokenService()


# Dependency untuk AuthService
def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    token_service: TokenService = Depends(get_token_service),
    session_service: SessionService = Depends(get_session_service),
    password_hasher: Argon2Hasher = Depends(get_password_hasher),
) -> AuthService:
    return AuthService(user_repo, token_service, session_service, password_hasher)


# OAuth2PasswordBearer dependency
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Dependency untuk get_current_user
async def get_current_user_dependency(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user
