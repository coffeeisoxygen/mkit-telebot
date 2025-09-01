from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.db_user import User  # noqa: F401

__all__ = ["User"]
