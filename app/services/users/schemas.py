from pydantic import BaseModel, Field


class UserBase(BaseModel):
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    full_name: str | None = Field(
        min_length=3, max_length=100, pattern=r"^[a-zA-Z\s]+$"
    )


class UserCreate(UserBase):
    password: str = Field(
        min_length=6,
        max_length=100,
        pattern=r"^[^\s]+$",
        alias="password",
    )


class UserRead(UserBase):
    id: int


class UserList(UserBase):
    pass
