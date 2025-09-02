from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TokenPayload(BaseModel):
    sub: str  # Userid ya bre
    username: str
    scopes: list[str]
    exp: datetime
    iat: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: str
    scopes: list[str]
