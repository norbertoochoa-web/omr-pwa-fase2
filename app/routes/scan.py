from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.scan import ScanRequest, ScanResponse
from app.routes.dependencies import get_current_user
from app.services.omr_service import process_omr_image
from app.services.template_service import get_template_by_name
from app.services.session_service import get_session

router = APIRouter()


@router.post("/scan", response_model=ScanResponse)
async def scan_omr(
    template_id: str = Form(...),
    session_id: str = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    import uuid
    import os
    from app.config import settings

    template = await get_template_by_name(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_ext = os.path.splitext(file.filename)[1] or ".jpg"
    unique_name = f"scan_{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_name)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    try:
        result = await process_omr_image(
            db,
            session_id=uuid.UUID(session_id) if session_id else None,
            image_id=uuid.uuid4(),
            template_id=template.id,
            image_path=file_path,
        )

        return ScanResponse(
            status=result["status"],
            file_name=file.filename,
            score=result.get("score"),
            answers=result.get("answers", {}),
            verdicts=result.get("verdicts"),
            error_message=result.get("error_message"),
        )

    except Exception as e:
        return ScanResponse(
            status="error",
            file_name=file.filename,
            score=None,
            answers={},
            verdicts=None,
            error_message=str(e),
        )
