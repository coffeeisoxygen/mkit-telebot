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
    logger.info(f"Cek user dengan username '{config.username}' di database...")
    user = await repo.get_by_username(config.username)
    logger.debug(f"Hasil query get_by_username: {user}")
    if user:
        if user.is_superuser and user.is_active:
            logger.info(
                f"Superuser aktif dengan username '{config.username}' sudah ada, tidak perlu seed."
            )
            logger.debug("Return False karena superuser sudah ada.")
            return False
        else:
            logger.warning(
                f"User dengan username '{config.username}' sudah ada, tapi belum superuser aktif."
            )
            # Optional: bisa update jadi superuser, atau hanya warning
            return False

    logger.info("Belum ada user admin, membuat default admin...")

    admin_data = {
        "username": config.username,
        "full_name": config.full_name,
        "hashed_password": hasher.hash_password(config.password),
        "is_active": config.is_active,
        "is_superuser": config.is_superuser,
    }

    try:
        logger.debug(f"Menjalankan query create admin: {admin_data}")
        await repo.create(admin_data)
        logger.debug("Menjalankan commit session.")
        await repo.session.commit()
    except IntegrityError:
        logger.debug("IntegrityError terjadi, rollback session.")
        await repo.session.rollback()
        logger.warning(f"Admin '{config.username}' sudah ada (race condition).")
        logger.debug("Return False karena IntegrityError.")
        return False
    except Exception as exc:
        logger.debug(f"Exception terjadi: {exc}, rollback session.")
        await repo.session.rollback()
        logger.error(f"Gagal membuat default admin: {exc}")
        logger.debug("Return False karena Exception.")
        return False
    else:
        logger.info(f"Default admin '{config.username}' berhasil dibuat.")
        logger.debug("Return True karena admin berhasil dibuat.")
        return True
