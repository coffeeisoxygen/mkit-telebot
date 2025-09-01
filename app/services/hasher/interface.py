from typing import Protocol


class IPasswordHasher(Protocol):
    """Interface untuk layanan hashing password."""

    def hash_password(self, password: str) -> str: ...

    def verify_password(self, password: str, hashed_password: str) -> bool: ...
