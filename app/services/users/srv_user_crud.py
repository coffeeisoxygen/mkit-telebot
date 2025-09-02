from loguru import logger
from sqlalchemy.exc import IntegrityError

from app.custom.exception.exceptions import UserDuplicateError
from app.models import User as Db_User
from app.repositories.repo_user import UserRepository
from app.schemas.sch_user import UserCreate, UserPublicResponse
from app.services.hasher.interface import IPasswordHasher


class UserCrudService:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: IPasswordHasher,
    ):
        self.user_repository: UserRepository = user_repository
        self.password_hasher: IPasswordHasher = password_hasher

    @logger.catch
    async def create_user(self, user_data: UserCreate) -> UserPublicResponse:
        # cek duplicate
        existing = await self.user_repository.get_by_username(user_data.username)
        if existing:
            raise UserDuplicateError(
                message=f"Username {user_data.username} sudah terpakai.",
                context={"username": user_data.username},
            )  # tidak perlu chaining di sini

        # hash password
        hashed_password = self.password_hasher.hash_password(user_data.password)

        # prepare dict untuk repo
        user_data_dict = user_data.model_dump(exclude={"password"})
        user_data_dict["hashed_password"] = hashed_password

        try:
            new_user: Db_User = await self.user_repository.create(user_data_dict)
            await self.user_repository.session.commit()
            logger.info(f"User {new_user.username} berhasil dibuat.")
            return UserPublicResponse.model_validate(new_user)
        except IntegrityError:
            await self.user_repository.session.rollback()
            logger.error(
                f"Username {user_data.username} sudah terpakai (IntegrityError)."
            )
            raise UserDuplicateError(
                message=f"Username {user_data.username} sudah terpakai.",
                context={"username": user_data.username},
            ) from None
        except Exception as e:
            await self.user_repository.session.rollback()
            logger.error(f"Error saat membuat user: {e}")
            raise
