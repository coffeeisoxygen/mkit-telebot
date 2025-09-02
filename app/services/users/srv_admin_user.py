from loguru import logger
from sqlalchemy.exc import IntegrityError

from app.models import User as Db_User
from app.repositories.repo_user import UserRepository
from app.schemas.sch_user import UserAdminResponse, UserAdminSeed
from app.services.hasher.interface import IPasswordHasher


class AdminUserService:
    def __init__(
        self, user_repository: UserRepository, password_hasher: IPasswordHasher
    ):
        self.user_repository: UserRepository = user_repository
        self.password_hasher: IPasswordHasher = password_hasher

    async def seed_default_admin(self) -> UserAdminResponse | None:
        """Membuat admin default jika belum ada superuser di database.

        Return UserPublicResponse jika berhasil, None jika sudah ada superuser.
        """
        logger.info("Cek keberadaan superuser di database...")
        stmt = Db_User.__table__.select().where(Db_User.is_superuser)
        result = await self.user_repository.session.execute(stmt)
        superuser = result.first()
        if superuser:
            logger.info("Superuser sudah ada, tidak perlu seed.")
            return None

        logger.info("Superuser belum ada, membuat default admin...")

        admin_seed = UserAdminSeed(
            username="admin",
            full_name="Default Admin",
            password="admin123",
        )
        admin_data = admin_seed.model_dump(exclude={"password"})
        admin_data["hashed_password"] = self.password_hasher.hash_password(
            admin_seed.password
        )
        admin_data["is_active"] = True
        admin_data["is_superuser"] = True
        try:
            new_admin = await self.user_repository.create(admin_data)
            await self.user_repository.session.commit()
            logger.info("Default admin berhasil dibuat.")
            return UserAdminResponse.model_validate(new_admin)
        except IntegrityError as exc:
            await self.user_repository.session.rollback()
            logger.error(f"Gagal membuat default admin: {exc}")
            return None
