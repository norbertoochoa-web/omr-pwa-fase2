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
    id: str
    name: str
    description: str | None
