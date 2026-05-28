import uuid
import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Template, Session, Image


async def create_session(
    db: AsyncSession,
    user_id: uuid.UUID,
    template_id: uuid.UUID,
    name: str,
) -> Session:
    session_obj = Session(
        user_id=user_id,
        template_id=template_id,
        name=name,
        status="ACTIVE",
    )
    db.add(session_obj)
    await db.flush()
    return session_obj


async def get_user_sessions(db: AsyncSession, user_id: uuid.UUID) -> list[Session]:
    result = await db.execute(
        select(Session).where(Session.user_id == user_id).order_by(Session.created_at.desc())
    )
    return list(result.scalars().all())


async def get_session(db: AsyncSession, session_id: uuid.UUID) -> Session | None:
    result = await db.execute(select(Session).where(Session.id == session_id))
    return result.scalar_one_or_none()


async def add_image_to_session(
    db: AsyncSession,
    session_id: uuid.UUID,
    filename: str,
    original_path: str,
) -> Image:
    image = Image(
        session_id=session_id,
        filename=filename,
        original_path=original_path,
        status="PENDING",
    )
    db.add(image)

    result = await db.execute(select(Session).where(Session.id == session_id))
    session_obj = result.scalar_one_or_none()
    if session_obj:
        session_obj.total_images += 1

    await db.flush()
    return image
