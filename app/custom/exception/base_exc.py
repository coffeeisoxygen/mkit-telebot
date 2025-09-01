from typing import Any


class AppExceptionError(Exception):
    """Base exception with adapter support and proper chaining."""

    default_message: str = "An application error occurred."
    status_code: int | None = None  # subclass wajib override

    def __init__(
        self,
        message: str | None = None,
        name: str = "ApplicationError",
        context: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        self.message = message or self.default_message
        self.name = name
        self.context = context or {}
        self.__cause__ = cause  # built-in chaining

        super().__init__(self._compose_message())

    def _compose_message(self) -> str:
        """Bikin message final dengan cause kalau ada."""
        if self.__cause__:
            return f"{self.message} (caused by {type(self.__cause__).__name__}: {self.__cause__})"
        return self.message

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "message": self.message,
            "status_code": self.status_code,
            "context": self.context,
            "cause": str(self.__cause__) if self.__cause__ else None,
        }

    def __str__(self) -> str:
        return self._compose_message()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} status={self.status_code} message={self.message!r}>"
