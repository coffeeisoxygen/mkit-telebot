from typing import Any

from app.exception.base_exc import AppExceptionError


class RequestValidationError(AppExceptionError):
    """Raised when request validation fails.

    This exception is used to indicate that the request data is invalid
    and does not conform to the expected schema.

    Args:
        AppExceptionError (_type_): _description_
    """

    default_message: str = "Request validation error occurred."
    status_code: int | None = 422


class IPBlockedError(AppExceptionError):
    """Exception kalau IP di-blacklist atau tidak allowed."""

    default_message: str = "Forbidden: IP address tidak diizinkan."
    status_code: int | None = 403

    def __init__(self, ip: str, endpoint: str, context: dict[str, Any] | None = None):
        ctx = context or {}
        ctx.update({"ip": ip, "endpoint": endpoint})

        super().__init__(
            message=self.default_message,
            context=ctx,
        )


# group related to internal services
class InternalServiceError(AppExceptionError):
    """Exception untuk kesalahan internal server."""

    default_message: str = "Internal server error occurred."
    status_code: int | None = 500


class EntityNotFoundError(InternalServiceError):
    """Exception untuk entitas yang tidak ditemukan."""

    default_message: str = "Entity not found."
    status_code: int | None = 404


# Group User exceptions Error
class UserGenericError(AppExceptionError):
    """Exception untuk kesalahan umum pada user."""

    default_message: str = "User error occurred."
    status_code: int | None = 400


class UserNotFoundError(UserGenericError):
    """Exception untuk user tidak ditemukan."""

    default_message: str = "User not found."
    status_code: int | None = 404


class UserDuplicateError(UserGenericError):
    """Exception untuk user duplikat."""

    default_message: str = "User already exists."
    status_code: int | None = 409


class UserCreationError(UserGenericError):
    """Exception untuk kesalahan saat membuat user."""

    default_message: str = "User creation failed."
    status_code: int | None = 400


class UserPasswordGenericError(UserGenericError):
    """Exception untuk kesalahan umum pada password user."""

    default_message: str = "User password error occurred."
    status_code: int | None = 400


class UserPasswordError(UserGenericError):
    """Exception untuk kesalahan saat mengubah password user."""

    default_message: str = "User password update failed."
    status_code: int | None = 400


class UserInActiveError(UserGenericError):
    """Exception untuk user tidak aktif."""

    default_message: str = "User is inactive."
    status_code: int | None = 403


class PasswordInternalError(AppExceptionError):
    """Exception untuk kesalahan internal pada password."""

    default_message: str = "Internal password error occurred."
    status_code: int | None = 500


# group token related
class TokenGenericError(AppExceptionError):
    """Exception untuk kesalahan umum pada token."""

    default_message: str = "Token error occurred."
    status_code: int | None = 400


class AuthError(AppExceptionError):
    """Exception untuk kesalahan autentikasi."""

    default_message: str = "Authentication error occurred."
    status_code: int | None = 401


class TokenNotFoundError(TokenGenericError):
    """Exception untuk token tidak ditemukan."""

    default_message: str = "Token not found."
    status_code: int | None = 404


class TokenExpiredError(TokenGenericError):
    """Exception untuk token yang sudah kedaluwarsa."""

    default_message: str = "Token expired."
    status_code: int | None = 401


class TokenInvalidError(TokenGenericError):
    """Exception untuk token yang tidak valid."""

    default_message: str = "Token invalid."
    status_code: int | None = 401


class SessionGenericError(AppExceptionError):
    """Exception untuk kesalahan umum pada session."""

    default_message: str = "Session error occurred."
    status_code: int | None = 400


class SessionLimitExceededError(SessionGenericError):
    """Exception untuk batas maksimum sesi yang terlampaui."""

    default_message: str = "Session limit exceeded."
    status_code: int | None = 429
