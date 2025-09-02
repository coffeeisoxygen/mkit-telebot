from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_session import Session as Db_Session


class SessionRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def create(self, obj_in: dict) -> Db_Session:
        db_session = Db_Session(**obj_in)
        self.session.add(db_session)
        await self.session.flush()
        return db_session

    async def get_by_id(self, obj_id: int) -> Db_Session | None:
        stmt = select(Db_Session).where(Db_Session.id == obj_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_token(self, token: str) -> Db_Session | None:
        stmt = select(Db_Session).where(Db_Session.token == token)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_by_user(self, user_id: int) -> list[Db_Session]:
        stmt = select(Db_Session).where(Db_Session.user_id == user_id)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update_activity(
        self, obj_id: int, last_activity: datetime
    ) -> Db_Session | None:
        db_session = await self.get_by_id(obj_id)
        if not db_session:
            return None
        db_session.last_activity = last_activity
        await self.session.flush()
        return db_session

    async def delete(self, obj_id: int) -> bool:
        db_session = await self.get_by_id(obj_id)
        if not db_session:
            return False
        await self.session.delete(db_session)
        await self.session.flush()
        return True

    async def set_active(
        self, obj_id: int, is_active: bool = True
    ) -> Db_Session | None:
        db_session = await self.get_by_id(obj_id)
        if not db_session:
            return None
        db_session.is_active = is_active
        await self.session.flush()
        return db_session
