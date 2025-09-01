from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.custom.exception.exceptions import UserNotFoundError
from app.models.db_user import User as Db_User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def create(self, obj_in: dict) -> Db_User:
        """Menciptakan entitas User baru di database."""
        from sqlalchemy.exc import IntegrityError

        from app.custom.exception.exceptions import UserDuplicateError

        db_user = Db_User(**obj_in)
        self.session.add(db_user)
        try:
            await self.session.flush()
        except IntegrityError as e:
            raise UserDuplicateError(
                message=f"User dengan username '{obj_in.get('username')}' sudah ada.",
                context={"username": obj_in.get("username")},
            ) from e
        return db_user

    async def get_by_id(self, obj_id: int) -> Db_User | None:
        """Mengambil entitas User berdasarkan ID.

        Mengembalikan None jika User tidak ditemukan.
        """
        stmt = select(Db_User).where(Db_User.id == obj_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Db_User | None:
        """Mengambil entitas User berdasarkan username.

        Mengembalikan None jika User tidak ditemukan.
        """
        stmt = select(Db_User).where(Db_User.username == username)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list(
        self,
        offset: int = 0,
        limit: int = 50,
        is_active: bool | None = None,
    ) -> list[Db_User]:
        """Mengambil daftar entitas User dengan paginasi dan filter aktif/nonaktif."""
        stmt = select(Db_User)
        if is_active is not None:
            stmt = stmt.where(Db_User.is_active == is_active)
        stmt = stmt.offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update(self, obj_id: int, obj_in: dict) -> Db_User:
        """Memperbarui entitas User berdasarkan ID.

        Melempar UserNotFoundError jika User tidak ditemukan.
        """
        db_user = await self.get_by_id(obj_id)
        if not db_user:
            raise UserNotFoundError(
                message=f"User dengan ID {obj_id} tidak ditemukan.",
                context={"user_id": obj_id},
            )
        for k, v in obj_in.items():
            setattr(db_user, k, v)
        await self.session.flush()
        return db_user

    async def delete(self, obj_id: int) -> bool:
        """Menghapus entitas User berdasarkan ID.

        Melempar UserNotFoundError jika User tidak ditemukan.
        """
        db_user = await self.get_by_id(obj_id)
        if not db_user:
            raise UserNotFoundError(
                message=f"User dengan ID {obj_id} tidak ditemukan.",
                context={"user_id": obj_id},
            )
        await self.session.delete(db_user)
        await self.session.flush()
        return True

    async def deactivate(self, obj_id: int) -> Db_User:
        """Menonaktifkan entitas User berdasarkan ID.

        Melempar UserNotFoundError jika User tidak ditemukan.
        """
        db_user = await self.get_by_id(obj_id)
        if not db_user:
            raise UserNotFoundError(
                message=f"User dengan ID {obj_id} tidak ditemukan.",
                context={"user_id": obj_id},
            )
        db_user.is_active = False
        await self.session.flush()
        return db_user
