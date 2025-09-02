from collections.abc import Callable
from functools import wraps

from fastapi import Request
from loguru import logger

from app.custom.exception import IPBlockedError, RequestValidationError


class IPFilter:
    def __init__(
        self,
        allowed_ips: set[str] | None = None,
        blocked_ips: set[str] | None = None,
        enabled: bool = True,
    ):
        r"""Inisialisasi IPFilter dengan daftar IP yang diizinkan atau diblokir.

        Args:
            allowed_ips (set[str] | None): Daftar IP yang diizinkan.
            blocked_ips (set[str] | None): Daftar IP yang diblokir.
            enabled (bool): Toggle global untuk mengaktifkan atau menonaktifkan filter IP.
        example:
            allowed_ips={"192.168.1.1", "192.168.1.2"},
            blocked_ips={"192.168.1.3"},
            enabled=True
        """
        self.allowed_ips = set(allowed_ips) if allowed_ips else None
        self.blocked_ips = set(blocked_ips) if blocked_ips else None
        self.enabled = enabled

        if self.allowed_ips and self.blocked_ips:
            raise ValueError(
                "Tidak bisa menggunakan allowed_ips dan blocked_ips secara bersamaan."
            )

    def is_valid(self, ip_address: str) -> bool:
        """Cek apakah IP valid sesuai rules."""
        if not self.enabled:
            return True
        if self.allowed_ips is not None:
            return ip_address in self.allowed_ips
        if self.blocked_ips is not None:
            return ip_address not in self.blocked_ips
        return True


# Decorator untuk memproteksi endpoint
def ip_protected(ip_filter: IPFilter):
    """Decorator untuk memproteksi endpoint berdasarkan IP.

    Args:
        ip_filter (IPFilter): Instance IPFilter dengan aturan IP.

    Returns:
        Callable: Decorator untuk endpoint FastAPI.
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")
            if not isinstance(request, Request):
                raise RequestValidationError(
                    message="Request object tidak ditemukan. ",
                    context={
                        "detail": "Pastikan endpoint mendefinisikan parameter 'request: Request'."
                    },
                    cause=TypeError("Parameter 'request' tidak ditemukan."),
                )

            client_ip = request.client.host if request.client else None
            if client_ip is None or not ip_filter.is_valid(client_ip):
                logger.warning(
                    f"Blokir request dari IP: {client_ip} di endpoint {func.__name__}"
                )
                # Ensure ip is always a string
                raise IPBlockedError(ip=client_ip or "unknown", endpoint=func.__name__)

            return await func(*args, **kwargs)

        return wrapper

    return decorator
