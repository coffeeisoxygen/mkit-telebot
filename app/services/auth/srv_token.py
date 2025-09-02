from datetime import UTC, datetime, timedelta

import jwt
from jwt import PyJWTError

from app.config import get_settings
from app.schemas import TokenData, TokenPayload, TokenResponse

settings = get_settings()


class TokenService:
    def __init__(self):
        self.secret_key = settings.JWT.secret_key
        self.algorithm = settings.JWT.algorithm
        self.expires_delta = timedelta(seconds=settings.JWT.access_token_expires)

    def create_token(
        self,
        user_id: int,
        username: str,
        scopes: list[str] | None = None,
    ) -> TokenResponse:
        now = datetime.now(UTC)
        expire = now + self.expires_delta

        payload = TokenPayload(
            sub=str(user_id),
            username=username,
            scopes=scopes or ["user"],
            iat=now,
            exp=expire,
        )
        encoded_jwt = jwt.encode(
            payload.model_dump(), self.secret_key, algorithm=self.algorithm
        )

        return TokenResponse(
            access_token=encoded_jwt,
            expires_in=int(self.expires_delta.total_seconds()),
        )

    def decode_token(self, token: str) -> TokenData | None:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return TokenData(
                user_id=int(payload["sub"]),
                username=payload["username"],
                scopes=payload.get("scopes", []),
            )
        except PyJWTError:
            return None

    def is_scope_allowed(self, token_data: TokenData, required_scope: str) -> bool:
        return required_scope in token_data.scopes
