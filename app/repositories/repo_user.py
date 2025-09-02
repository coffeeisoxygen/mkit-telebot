from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_user import User as Db_User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def create(self, obj_in: dict) -> Db_User:
        """Insert user baru ke database (tanpa commit, biar service yang handle)."""
        db_user = Db_User(**obj_in)
        self.session.add(db_user)
        await self.session.flush()  # dapat id dari DB
        return db_user

    async def get_by_id(self, obj_id: int) -> Db_User | None:
        """Ambil user berdasarkan ID, return None kalau gak ada."""
        stmt = select(Db_User).where(Db_User.id == obj_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Db_User | None:
        """Ambil user berdasarkan username, return None kalau gak ada."""
        stmt = select(Db_User).where(Db_User.username == username)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list(
        self,
        offset: int = 0,
        limit: int = 50,
        is_active: bool | None = None,
    ) -> list[Db_User]:
        """Ambil daftar user (bisa difilter active/non-active)."""
        stmt = select(Db_User)
        if is_active is not None:
            stmt = stmt.where(Db_User.is_active == is_active)
        stmt = stmt.offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update(self, obj_id: int, obj_in: dict) -> Db_User | None:
        """Update user by id, return None kalau gak ada."""
        db_user = await self.get_by_id(obj_id)
        if not db_user:
            return None
        for k, v in obj_in.items():
            setattr(db_user, k, v)
        await self.session.flush()
        return db_user

    async def delete(self, obj_id: int) -> bool:
        """Delete user by id, return False kalau gak ada."""
        db_user = await self.get_by_id(obj_id)
        if not db_user:
            return False
        await self.session.delete(db_user)
        await self.session.flush()
        return True

    async def deactivate(self, obj_id: int) -> Db_User | None:
        """Set user jadi inactive, return None kalau gak ada."""
        db_user = await self.get_by_id(obj_id)
        if not db_user:
            return None
        db_user.is_active = False
        await self.session.flush()
        return db_user
