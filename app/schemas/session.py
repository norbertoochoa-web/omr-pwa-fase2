import uuid
import datetime
from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    name: str
    template_id: str


class SessionResponse(BaseModel):
    id: uuid.UUID
    name: str
    status: str
    total_images: int
    processed_images: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class SessionDetailResponse(SessionResponse):
    template_id: uuid.UUID
    user_id: uuid.UUID
    result_txt_path: str | None
