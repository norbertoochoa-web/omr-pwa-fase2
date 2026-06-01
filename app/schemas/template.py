from pydantic import BaseModel


class TemplateCreate(BaseModel):
    name: str
    description: str | None = None
    institution_id: str | None = None
    page_width: int
    page_height: int
    bubble_width: int
    bubble_height: int
    template_data: dict
    evaluation_data: dict | None = None
    config: dict | None = None
    marker_image_path: str | None = None


class TemplateResponse(BaseModel):
    id: str
    name: str
    institution_id: str | None = None
    description: str | None = None
    page_width: int
    page_height: int
    bubble_width: int
    bubble_height: int
    config: dict
    template_data: dict
    evaluation_data: dict | None = None
    marker_image_path: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
