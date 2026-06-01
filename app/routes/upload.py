import os
import shutil
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import settings
from app.schemas.upload import UploadResponse
from app.routes.dependencies import get_current_user
from app.services.session_service import add_image_result, get_session
from app.services.omr_service import process_single_image_sync
from app.services.template_service import get_template_by_name

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_and_process(
    session_id: str = Form(...),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    session_obj = await get_session(db, uuid.UUID(session_id))
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")

    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image format")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_ext = os.path.splitext(image.filename or "capture.jpg")[1] or ".jpg"
    unique_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_name)

    content = await image.read()
    with open(file_path, "wb") as f:
        f.write(content)

    img_id = uuid.uuid4()

    template = await get_template_by_name(db, "imax_evaluacion")
    if not template:
        result_data = {"status": "error", "error_message": "Default template not configured"}
    else:
        if not session_obj.institution_id and template.institution_id:
            session_obj.institution_id = template.institution_id
        inst_dir = session_obj.institution_id or "default"
        session_dir = os.path.join(settings.OUTPUTS_DIR, inst_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)
        marked_path = os.path.join(session_dir, f"{img_id}_marked.jpg")
        original_path = os.path.join(session_dir, f"{img_id}_original{file_ext}")
        shutil.copy2(file_path, original_path)
        result_data = await process_single_image_sync(
            db, uuid.UUID(session_id), image.filename, file_path, template.id,
            marked_path=marked_path,
        )

    img_record = await add_image_result(
        db,
        session_id=uuid.UUID(session_id),
        filename=image.filename,
        original_path=file_path,
        image_id=img_id,
        answers=result_data.get("answers"),
        score=result_data.get("score"),
        total_questions=result_data.get("total"),
        verdicts=result_data.get("verdicts"),
        error_message=result_data.get("error_message"),
        sequenced_id=f"A{session_obj.total_images + 1:03d}",
    )

    return UploadResponse(
        image_id=str(img_record.id),
        status=result_data.get("status", "error"),
        answers=result_data.get("answers"),
        score=result_data.get("score"),
        total=result_data.get("total"),
        error_message=result_data.get("error_message"),
    )
