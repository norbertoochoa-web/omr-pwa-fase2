from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.template import TemplateCreate, TemplateResponse
from app.routes.dependencies import get_current_user
from app.services.template_service import create_template, get_template_by_id, list_templates

router = APIRouter()


@router.post("/templates", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_new_template(
    data: TemplateCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    template = await create_template(db, data.model_dump())
    return TemplateResponse(
        id=str(template.id),
        name=template.name,
        institution_id=template.institution_id,
        description=template.description,
        page_width=template.page_width,
        page_height=template.page_height,
        bubble_width=template.bubble_width,
        bubble_height=template.bubble_height,
        config=template.config,
        template_data=template.template_data,
        evaluation_data=template.evaluation_data,
        marker_image_path=template.marker_image_path,
        created_at=template.created_at.isoformat() if template.created_at else None,
        updated_at=template.updated_at.isoformat() if template.updated_at else None,
    )


@router.get("/templates", response_model=list[TemplateResponse])
async def get_templates(
    institution_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    templates = await list_templates(db, institution_id=institution_id)
    return [
        TemplateResponse(
            id=str(t.id),
            name=t.name,
            institution_id=t.institution_id,
            description=t.description,
            page_width=t.page_width,
            page_height=t.page_height,
            bubble_width=t.bubble_width,
            bubble_height=t.bubble_height,
            config=t.config,
            template_data=t.template_data,
            evaluation_data=t.evaluation_data,
            marker_image_path=t.marker_image_path,
            created_at=t.created_at.isoformat() if t.created_at else None,
            updated_at=t.updated_at.isoformat() if t.updated_at else None,
        )
        for t in templates
    ]


@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    from uuid import UUID
    template = await get_template_by_id(db, UUID(template_id))
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return TemplateResponse(
        id=str(template.id),
        name=template.name,
        institution_id=template.institution_id,
        description=template.description,
        page_width=template.page_width,
        page_height=template.page_height,
        bubble_width=template.bubble_width,
        bubble_height=template.bubble_height,
        config=template.config,
        template_data=template.template_data,
        evaluation_data=template.evaluation_data,
        marker_image_path=template.marker_image_path,
        created_at=template.created_at.isoformat() if template.created_at else None,
        updated_at=template.updated_at.isoformat() if template.updated_at else None,
    )
