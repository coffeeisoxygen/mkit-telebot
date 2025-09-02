from loguru import logger
from sqlalchemy.exc import IntegrityError

from app.config.values import ConfigAdminAccount
from app.repositories.repo_user import UserRepository
from app.schemas.sch_user import UserAdminResponse
from app.services.hasher.interface import IPasswordHasher


async def seed_default_admin(
    repo: UserRepository,
    hasher: IPasswordHasher,
    config: ConfigAdminAccount,
) -> UserAdminResponse | None:
    """Membuat admin default jika belum ada superuser aktif di database.

    Return UserAdminResponse jika berhasil, None jika sudah ada superuser.
    """
    logger.info("Cek keberadaan superuser di database...")
    superuser = await repo.get_active_superuser()
    if superuser:
        logger.info("Superuser sudah ada, tidak perlu seed.")
        return None

    logger.info("Superuser belum ada, membuat default admin...")

    admin_data = {
        "username": config.username,
        "full_name": config.full_name,
        "hashed_password": hasher.hash_password(config.password),
        "is_active": config.is_active,
        "is_superuser": config.is_superuser,
    }

    try:
        new_admin = await repo.create(admin_data)
        await repo.session.commit()
        logger.info(f"Default admin '{config.username}' berhasil dibuat.")
        return UserAdminResponse.model_validate(new_admin)
    except IntegrityError:
        await repo.session.rollback()
        logger.warning(f"Admin '{config.username}' sudah ada (race condition).")
        return None
    except Exception as exc:
        await repo.session.rollback()
        logger.error(f"Gagal membuat default admin: {exc}")
        raise
