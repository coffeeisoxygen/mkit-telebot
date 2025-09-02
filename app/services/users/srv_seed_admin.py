from loguru import logger
from sqlalchemy.exc import IntegrityError

from app.config.values import ConfigAdminAccount
from app.repositories.repo_user import UserRepository
from app.services.hasher.interface import IPasswordHasher


async def seed_default_admin(
    repo: UserRepository,
    hasher: IPasswordHasher,
    config: ConfigAdminAccount,
) -> bool:
    """Membuat default admin user jika belum ada superuser aktif di database.

    Return True jika berhasil, False jika sudah ada atau gagal.
    """
    log = logger.bind(action="seed_admin", username=config.username)
    log.info("Cek superuser aktif di database...")

    async with repo.session.begin():
        superuser = await repo.get_active_superuser()
        log = log.bind(superuser_exists=bool(superuser))
        if superuser:
            log.info("Sudah ada superuser aktif, tidak perlu seed.")
            return False

        log.info("Belum ada superuser aktif, cek username...")
        existing = await repo.get_by_username(config.username)
        log = log.bind(existing=bool(existing))
        if existing:
            log.warning("Username admin sudah dipakai user lain, seed dibatalkan.")
            return False

        admin_data = {
            "username": config.username,
            "full_name": config.full_name,
            "hashed_password": hasher.hash_password(config.password),
            "is_active": config.is_active,
            "is_superuser": config.is_superuser,
        }
        log = log.bind(admin_data=admin_data)
        try:
            log.info("Membuat default admin...")
            await repo.create(admin_data)
        except IntegrityError as e:
            log = log.bind(error=str(e))
            log.warning("Admin sudah ada (race condition), rollback otomatis.")
            return False
        except Exception as exc:
            log = log.bind(error=str(exc))
            log.exception("Gagal membuat default admin.")
            raise
        else:
            log.info("Default admin berhasil dibuat.")
            return True
