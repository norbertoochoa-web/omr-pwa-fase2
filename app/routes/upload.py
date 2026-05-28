from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.scan import UploadResponse
from app.routes.dependencies import get_current_user
from app.services.session_service import add_image_to_session, get_session

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_image(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    import uuid
    import os
    from app.config import settings

    session_obj = await get_session(db, uuid.UUID(session_id))
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_ext = os.path.splitext(file.filename)[1] or ".jpg"
    unique_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_name)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    image = await add_image_to_session(db, uuid.UUID(session_id), file.filename, file_path)

    return UploadResponse(
        image_id=str(image.id),
        session_id=session_id,
        filename=file.filename,
        status=image.status,
    )
