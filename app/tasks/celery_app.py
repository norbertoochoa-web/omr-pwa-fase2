import uuid
import asyncio

from celery import Celery
from sqlalchemy import select

from app.config import settings
from app.database import async_session_factory
from app.models import Image as ImageModel, Session

celery_app = Celery(
    "omr_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def process_image_task(self, session_id: str, image_id: str, template_id: str, image_path: str):
    async def _process():
        from app.services.omr_service import process_omr_image

        async with async_session_factory() as db:
            try:
                result = await process_omr_image(
                    db,
                    uuid.UUID(session_id),
                    uuid.UUID(image_id),
                    uuid.UUID(template_id),
                    image_path,
                )

                result_img = await db.execute(
                    select(ImageModel).where(ImageModel.id == uuid.UUID(image_id))
                )
                img = result_img.scalar_one_or_none()
                if img:
                    if result["status"] == "success":
                        img.status = "SUCCESS"
                        img.answer = result.get("answers")
                        img.score = result.get("score")
                        img.verdicts = result.get("verdicts")
                        img.processed_path = result.get("processed_path")
                    else:
                        img.status = "FAILED"
                        img.error_message = result.get("error_message")

                    session_result = await db.execute(
                        select(Session).where(Session.id == uuid.UUID(session_id))
                    )
                    session_obj = session_result.scalar_one_or_none()
                    if session_obj:
                        session_obj.processed_images += 1

                await db.commit()
                return result

            except Exception as e:
                await db.rollback()
                result_img = await db.execute(
                    select(ImageModel).where(ImageModel.id == uuid.UUID(image_id))
                )
                img = result_img.scalar_one_or_none()
                if img:
                    img.status = "FAILED"
                    img.error_message = str(e)
                await db.commit()
                raise

    return _run_async(_process())
