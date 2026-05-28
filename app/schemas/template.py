import uuid
from pydantic import BaseModel


class TemplateCreate(BaseModel):
    name: str
    description: str | None = None
    page_width: int
    page_height: int
    bubble_width: int
    bubble_height: int
    config: dict = {}
    template_data: dict
    evaluation_data: dict | None = None


class TemplateResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    page_width: int
    page_height: int

    class Config:
        from_attributes = True


class TemplateDetailResponse(TemplateResponse):
    config: dict
    template_data: dict
    evaluation_data: dict | None
