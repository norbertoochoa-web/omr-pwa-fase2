import uuid
import datetime
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user_id: str
    username: str
    full_name: str
    subscription_status: str


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    full_name: str | None
    subscription_status: str
    is_active: bool

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    user_id: str
    username: str
    exp: datetime.datetime
