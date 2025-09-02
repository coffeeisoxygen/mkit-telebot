from loguru import logger

from app.custom.exception.exceptions import (
    SessionGenericError,
    TokenInvalidError,
    UserInActiveError,
    UserNotFoundError,
    UserPasswordError,
)
from app.repositories.repo_user import UserRepository
from app.schemas.sch_user import UserInDB, UserLogin
from app.services.auth.srv_session import SessionService
from app.services.auth.srv_token import TokenService
from app.services.hasher.interface import IPasswordHasher


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        token_service: TokenService,
        session_service: SessionService,
        password_hasher: IPasswordHasher,
    ):
        self.user_repo = user_repo
        self.token_service = token_service
        self.session_service = session_service
        self.password_hasher = password_hasher

    async def authenticate_user(self, login_data: UserLogin) -> UserInDB:
        user = await self.user_repo.get_by_username(login_data.username)
        if not user:
            logger.warning(f"User not found: {login_data.username}")
            raise UserNotFoundError()
        if not user.is_active:
            logger.warning(f"User inactive: {login_data.username}")
            raise UserInActiveError()
        if not self.password_hasher.verify_password(
            login_data.password, user.hashed_password
        ):
            logger.warning(f"Invalid password for user: {login_data.username}")
            raise UserPasswordError()
        # Konversi ke UserInDB
        return UserInDB.model_validate(user)

    async def login(
        self,
        login_data: UserLogin,
        ip_address: str,
        user_agent: str,
    ):
        user = await self.authenticate_user(login_data)
        if user.id is None:
            logger.warning(f"User ID is None for user: {user.username}")
            raise UserNotFoundError("User ID is missing")
        token_resp = await self.token_service.create_token(
            user_id=user.id,
            username=user.username,
            scopes=["user"] if not user.is_superuser else ["admin", "user"],
        )
        session = await self.session_service.create_session(
            user_id=user.id,
            token=token_resp.access_token,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        logger.bind(user_id=user.id, username=user.username).info("User login success")
        return {
            "access_token": token_resp.access_token,
            "expires_in": token_resp.expires_in,
            "session_id": session.id,
        }

    async def logout(self, session_id: int):
        try:
            await self.session_service.deactivate_session(session_id)
        except SessionGenericError:
            logger.bind(session_id=session_id).warning("Logout failed: session error")
            raise
        else:
            logger.bind(session_id=session_id).info("User logout success")
            return True

    async def get_current_user(self, token: str) -> UserInDB:
        token_data = await self.token_service.decode_token(token)
        if not token_data:
            logger.warning("Invalid token")
            raise TokenInvalidError()
        user = await self.user_repo.get_by_id(token_data.user_id)
        if not user:
            logger.warning(f"User not found: {token_data.user_id}")
            raise UserNotFoundError()
        if not user.is_active:
            logger.warning(f"User inactive: {user.username}")
            raise UserInActiveError()
        # Konversi ke UserInDB
        return UserInDB.model_validate(user)
