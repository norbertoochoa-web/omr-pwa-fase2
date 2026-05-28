from pydantic import BaseModel


class UploadResponse(BaseModel):
    image_id: str
    status: str
    answers: dict | None = None
    score: float | None = None
    total: int | None = None
    error_message: str | None = None
