from datetime import datetime

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

    username: str = Field(min_length=3, max_length=50)
    full_name: str | None = Field(min_length=3, max_length=100)


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=100)


class UserInDB(UserBase):
    id: int | None = None
    password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime | None = None


class UserPublicResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime


class UserListResponse(BaseModel):
    users: list[UserPublicResponse]


class UserAdminSeed(UserCreate):
    is_superuser: bool = True
    is_active: bool = True


class UserAdminResponse(UserInDB):
    pass
