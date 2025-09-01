from loguru import logger

from app.custom.exception.exceptions import UserDuplicateError
from app.repositories.repo_user import Db_User, UserRepository
from app.services.hasher.interface import IPasswordHasher
from app.services.users.schemas import UserCreate


class UserService:
    def __init__(
        self, user_repository: UserRepository, password_hasher: IPasswordHasher
    ):
        self.user_repository: UserRepository = user_repository
        self.password_hasher: IPasswordHasher = password_hasher

    @logger.catch
    async def create_user(self, user_data: UserCreate) -> Db_User:
        from sqlalchemy.exc import IntegrityError

        # Ubah objek Pydantic menjadi dictionary yang dapat dimodifikasi
        user_data_dict = user_data.model_dump()

        # Hashing password dan mengganti nilai di dictionary
        plain_password = user_data_dict.pop("password")
        if plain_password:
            user_data_dict["hashed_password"] = self.password_hasher.hash_password(
                plain_password
            )

        try:
            return await self.user_repository.create(user_data_dict)
        except IntegrityError as e:
            raise UserDuplicateError(
                message=f"User dengan username '{user_data.username}' sudah ada.",
                context={"username": user_data.username},
            ) from e
