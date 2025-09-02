from loguru import logger
from sqlalchemy.exc import IntegrityError

from app.config.values import ConfigAdminAccount
from app.repositories.repo_user import UserRepository
from app.schemas.sch_user import UserAdminResponse  # optional untuk return
from app.services.hasher.interface import IPasswordHasher


class AdminSeedService:
    def __init__(
        self, user_repository: UserRepository, password_hasher: IPasswordHasher
    ):
        self.repo = user_repository
        self.hasher = password_hasher

    async def seed_default_admin(
        self, config: ConfigAdminAccount
    ) -> UserAdminResponse | None:
        """Membuat admin default jika belum ada superuser aktif di database."""
        logger.info("Cek keberadaan superuser di database...")
        superuser = await self.repo.get_active_superuser()
        if superuser:
            logger.info("Superuser sudah ada, tidak perlu seed.")
            return None

        logger.info("Superuser belum ada, membuat default admin...")

        admin_data = {
            "username": config.username,
            "full_name": config.full_name,
            "hashed_password": self.hasher.hash_password(config.password),
            "is_active": config.is_active,
            "is_superuser": config.is_superuser,
        }

        try:
            new_admin = await self.repo.create(admin_data)
            await self.repo.session.commit()
            logger.info(f"Default admin '{config.username}' berhasil dibuat.")
            # optional return Pydantic response untuk logging / test
            return UserAdminResponse.model_validate(new_admin)
        except IntegrityError:
            await self.repo.session.rollback()
            logger.warning(f"Admin '{config.username}' sudah ada (race condition).")
            return None
        except Exception as exc:
            await self.repo.session.rollback()
            logger.error(f"Gagal membuat default admin: {exc}")
            raise
