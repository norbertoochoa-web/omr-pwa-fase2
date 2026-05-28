from pydantic import BaseModel


class ScanRequest(BaseModel):
    template_id: str


class ScanResponse(BaseModel):
    status: str
    file_name: str
    score: float | None
    answers: dict
    verdicts: dict | None
    error_message: str | None = None


class UploadResponse(BaseModel):
    image_id: str
    session_id: str
    filename: str
    status: str
