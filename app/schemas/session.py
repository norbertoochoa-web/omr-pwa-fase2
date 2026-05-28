import uuid
import datetime
from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    name: str | None = None


class CreateSessionResponse(BaseModel):
    session_token: str
    status: str


class SessionResponse(BaseModel):
    id: str
    name: str | None
    status: str
    total_images: int
    processed_images: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    email_sent: bool


class FinishSessionResponse(BaseModel):
    status: str
    emailed: bool
    txt_filename: str
