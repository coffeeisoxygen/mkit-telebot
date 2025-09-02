from datetime import datetime, timedelta

from loguru import logger

from app.custom.exception.exceptions import (
    EntityNotFoundError,
    SessionGenericError,
)
from app.repositories.repo_session import SessionRepository
from app.schemas import (
    SessionCreate,
    SessionInDB,
)


class SessionService:
    def __init__(self, session_repository: SessionRepository):
        self.repo: SessionRepository = session_repository

    async def create_session(
        self,
        user_id: int,
        token: str,
        ip_address: str,
        user_agent: str,
        expires_in: int | None = 3600,
    ) -> SessionInDB:
        expires_at = (
            datetime.now() + timedelta(seconds=expires_in) if expires_in else None
        )
        try:
            session_data = SessionCreate(
                user_id=user_id,
                token=token,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=expires_at,
            )
            db_session = await self.repo.create(session_data.model_dump())
            logger.bind(user_id=user_id, token=token).info("Session created")
            return SessionInDB.model_validate(db_session)
        except Exception as e:
            logger.bind(user_id=user_id, token=token).error(
                f"Failed to create session: {e}"
            )
            raise SessionGenericError("Failed to create session") from e

    async def get_session_by_token(self, token: str) -> SessionInDB | None:
        db_session = await self.repo.get_by_token(token)
        if not db_session:
            logger.bind(token=token).warning("Session not found")
            raise EntityNotFoundError("Session not found")
        if not db_session.is_active:
            logger.bind(token=token).warning("Session inactive")
            raise SessionGenericError("Session is inactive")
        if db_session.expires_at and db_session.expires_at < datetime.now():
            db_session.is_active = False
            logger.bind(token=token).warning("Session expired")
            raise SessionGenericError("Session expired")
        return SessionInDB.model_validate(db_session)

    async def refresh_activity(self, session_id: int) -> SessionInDB | None:
        updated = await self.repo.update_activity(session_id, datetime.now())
        if updated:
            logger.bind(session_id=session_id).info("Session activity refreshed")
            return SessionInDB.model_validate(updated)
        logger.bind(session_id=session_id).warning(
            "Session not found for refresh_activity"
        )
        raise EntityNotFoundError("Session not found")

    async def deactivate_session(self, session_id: int) -> SessionInDB | None:
        updated = await self.repo.set_active(session_id, False)
        if updated:
            logger.bind(session_id=session_id).info("Session deactivated")
            return SessionInDB.model_validate(updated)
        logger.bind(session_id=session_id).warning("Session not found for deactivate")
        raise EntityNotFoundError("Session not found")

    async def delete_session(self, session_id: int) -> bool:
        result = await self.repo.delete(session_id)
        if result:
            logger.bind(session_id=session_id).info("Session deleted")
            return True
        logger.bind(session_id=session_id).warning("Session not found for delete")
        raise EntityNotFoundError("Session not found")

    async def list_sessions_by_user(self, user_id: int) -> list[SessionInDB]:
        sessions = await self.repo.list_by_user(user_id)
        logger.bind(user_id=user_id, count=len(sessions)).info("List sessions by user")
        return [SessionInDB.model_validate(s) for s in sessions]

    async def list_active_sessions(self) -> list[SessionInDB]:
        sessions = await self.repo.list_active_sessions()
        logger.bind(count=len(sessions)).info("List active sessions")
        return [SessionInDB.model_validate(s) for s in sessions]

    async def update_expiry(
        self, session_id: int, expires_in: int
    ) -> SessionInDB | None:
        db_session = await self.repo.get_by_id(session_id)
        if not db_session:
            logger.bind(session_id=session_id).warning(
                "Session not found for update_expiry"
            )
            raise EntityNotFoundError("Session not found")
        db_session.expires_at = datetime.now() + timedelta(seconds=expires_in)
        await self.repo.session.flush()
        logger.bind(session_id=session_id).info("Session expiry updated")
        return SessionInDB.model_validate(db_session)

    async def reactivate_session(self, session_id: int) -> SessionInDB | None:
        updated = await self.repo.set_active(session_id, True)
        if updated:
            logger.bind(session_id=session_id).info("Session reactivated")
            return SessionInDB.model_validate(updated)
        logger.bind(session_id=session_id).warning("Session not found for reactivate")
        raise EntityNotFoundError("Session not found")
