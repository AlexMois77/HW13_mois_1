from pydantic import BaseModel, EmailStr
from enum import Enum


class RoleEnum(Enum):
    USER = "user"
    ADMIN = "admin"


class RoleBase(BaseModel):
    id: int
    name: RoleEnum

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    role: RoleBase | None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
