import uuid
import datetime
from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class SubscriptionObject(BaseModel):
    status: str
    max_images: int
    expires: str | None = None


class LoginResponse(BaseModel):
    token: str
    user_id: str
    subscription: SubscriptionObject


class TokenData(BaseModel):
    user_id: str
    email: str
    exp: datetime.datetime
