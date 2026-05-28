from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Template as TemplateModel
from app.schemas.template import TemplateResponse, TemplateDetailResponse, TemplateCreate
from app.routes.dependencies import get_current_user
from app.services.template_service import create_template, get_template_by_name, get_template_by_id, list_templates

router = APIRouter()


@router.get("/templates", response_model=list[TemplateResponse])
async def list_all_templates(
    db: AsyncSession = Depends(get_db),
    _user_id: str = Depends(get_current_user),
):
    return await list_templates(db)


@router.get("/templates/{template_id}", response_model=TemplateDetailResponse)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
    _user_id: str = Depends(get_current_user),
):
    import uuid
    try:
        uid = uuid.UUID(template_id)
    except ValueError:
        template = await get_template_by_name(db, template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        uid = template.id

    template = await get_template_by_id(db, uid)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return TemplateDetailResponse(
        id=template.id,
        name=template.name,
        description=template.description,
        page_width=template.page_width,
        page_height=template.page_height,
        config=template.config,
        template_data=template.template_data,
        evaluation_data=template.evaluation_data,
    )


@router.post("/templates", response_model=TemplateDetailResponse, status_code=201)
async def create_new_template(
    request: TemplateCreate,
    db: AsyncSession = Depends(get_db),
    _user_id: str = Depends(get_current_user),
):
    existing = await get_template_by_name(db, request.name)
    if existing:
        raise HTTPException(status_code=400, detail="Template name already exists")

    template = await create_template(db, request.model_dump())
    return TemplateDetailResponse(
        id=template.id,
        name=template.name,
        description=template.description,
        page_width=template.page_width,
        page_height=template.page_height,
        config=template.config,
        template_data=template.template_data,
        evaluation_data=template.evaluation_data,
    )
