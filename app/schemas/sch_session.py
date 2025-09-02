from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseSessionModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class SessionCreate(BaseSessionModel):
    user_id: int
    token: str
    ip_address: str
    user_agent: str


class SessionInDB(BaseSessionModel):
    id: int
    user_id: int
    token: str
    ip_address: str
    user_agent: str
    last_activity: datetime
    created_at: datetime
    is_active: bool
    expires_at: datetime | None


class SessionUpdateActivity(BaseSessionModel):
    id: int
    last_activity: datetime


class SessionSetActive(BaseSessionModel):
    id: int
    is_active: bool
