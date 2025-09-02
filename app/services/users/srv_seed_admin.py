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
    """Membuat admin default jika belum ada superuser aktif di database.

    Return True jika berhasil, False jika sudah ada superuser atau gagal.
    """
    logger.info("Cek keberadaan superuser di database...")
    superuser = await repo.get_active_superuser()
    if superuser:
        logger.info("Superuser sudah ada, tidak perlu seed.")
        return False

    logger.info("Superuser belum ada, membuat default admin...")

    admin_data = {
        "username": config.username,
        "full_name": config.full_name,
        "hashed_password": hasher.hash_password(config.password),
        "is_active": config.is_active,
        "is_superuser": config.is_superuser,
    }

    try:
        await repo.create(admin_data)
        await repo.session.commit()
    except IntegrityError:
        await repo.session.rollback()
        logger.warning(f"Admin '{config.username}' sudah ada (race condition).")
        return False
    except Exception as exc:
        await repo.session.rollback()
        logger.error(f"Gagal membuat default admin: {exc}")
        return False
    else:
        logger.info(f"Default admin '{config.username}' berhasil dibuat.")
        return True
