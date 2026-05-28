import uuid
import json
import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Template


async def create_template(db: AsyncSession, template_data: dict) -> Template:
    template = Template(
        name=template_data["name"],
        description=template_data.get("description"),
        page_width=template_data["page_width"],
        page_height=template_data["page_height"],
        bubble_width=template_data["bubble_width"],
        bubble_height=template_data["bubble_height"],
        config=template_data.get("config", {}),
        template_data=template_data["template_data"],
        evaluation_data=template_data.get("evaluation_data"),
        marker_image_path=template_data.get("marker_image_path"),
    )
    db.add(template)
    await db.flush()
    return template


async def get_template_by_name(db: AsyncSession, name: str) -> Template | None:
    result = await db.execute(select(Template).where(Template.name == name))
    return result.scalar_one_or_none()


async def get_template_by_id(db: AsyncSession, template_id: uuid.UUID) -> Template | None:
    result = await db.execute(select(Template).where(Template.id == template_id))
    return result.scalar_one_or_none()


async def list_templates(db: AsyncSession) -> list[Template]:
    result = await db.execute(select(Template).order_by(Template.name))
    return list(result.scalars().all())
