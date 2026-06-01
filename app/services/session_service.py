import uuid
import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Session, Image


async def create_session(db: AsyncSession, user_id: uuid.UUID, name: str | None = None) -> Session:
    session_obj = Session(
        user_id=user_id,
        name=name or f"Sesión {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
        status="OPEN",
    )
    db.add(session_obj)
    await db.flush()
    await db.refresh(session_obj)
    return session_obj


async def get_session(db: AsyncSession, session_id: uuid.UUID) -> Session | None:
    result = await db.execute(select(Session).where(Session.id == session_id))
    return result.scalar_one_or_none()


async def get_user_sessions(db: AsyncSession, user_id: uuid.UUID) -> list[Session]:
    result = await db.execute(
        select(Session).where(Session.user_id == user_id).order_by(Session.created_at.desc())
    )
    return list(result.scalars().all())


async def add_image_result(
    db: AsyncSession,
    session_id: uuid.UUID,
    filename: str,
    original_path: str,
    image_id: uuid.UUID | None = None,
    answers: dict | None = None,
    score: float | None = None,
    total_questions: int | None = None,
    verdicts: dict | None = None,
    error_message: str | None = None,
    sequenced_id: str | None = None,
) -> Image:
    session_obj = await get_session(db, session_id)
    if not session_obj:
        raise ValueError("Session not found")

    image = Image(
        id=image_id or uuid.uuid4(),
        session_id=session_id,
        filename=filename,
        original_path=original_path,
        sequenced_id=sequenced_id,
        status="SUCCESS" if not error_message else "FAILED",
        answers=answers,
        score=score,
        total_questions=total_questions,
        verdicts=verdicts,
        error_message=error_message,
    )
    db.add(image)

    session_obj.total_images += 1
    session_obj.processed_images += 1
    await db.flush()
    await db.refresh(image)
    return image


async def finish_session(db: AsyncSession, session_id: uuid.UUID) -> Session:
    session_obj = await get_session(db, session_id)
    if not session_obj:
        raise ValueError("Session not found")

    session_obj.status = "COMPLETED"
    await db.flush()
    await db.refresh(session_obj)
    return session_obj
