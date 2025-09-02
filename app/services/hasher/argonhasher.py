from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.services.hasher.interface import IPasswordHasher


class Argon2Hasher(IPasswordHasher):
    def __init__(self):
        self.ph = PasswordHasher()

    def hash_password(self, password: str) -> str:
        """Menghash password menggunakan Argon2."""
        return self.ph.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Memverifikasi password dengan hash."""
        try:
            self.ph.verify(hashed_password, password)
        except VerifyMismatchError:
            return False
        else:
            return True
