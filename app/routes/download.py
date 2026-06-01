from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Session as SessionModel
from app.routes.dependencies import get_current_user

router = APIRouter()


@router.get("/sessions/{session_id}/download")
async def download_session_txt(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    import uuid
    import os
    from sqlalchemy import select

    result = await db.execute(
        select(SessionModel).where(SessionModel.id == uuid.UUID(session_id)).options(selectinload(SessionModel.images))
    )
    session_obj = result.scalar_one_or_none()
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")

    if session_obj.result_txt_path and os.path.exists(session_obj.result_txt_path):
        file_path = session_obj.result_txt_path
    else:
        from app.services.txt_service import generate_delphi_txt, save_txt_to_file
        from app.config import settings
        txt_content = generate_delphi_txt(session_obj)
        inst_dir = session_obj.institution_id or "default"
        session_dir = os.path.join(settings.OUTPUTS_DIR, inst_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)
        file_path = save_txt_to_file(txt_content, session_dir, str(session_obj.id))
        session_obj.result_txt_path = file_path

    return FileResponse(
        file_path,
        filename=f"{session_obj.id}.txt",
        media_type="application/octet-stream",
    )
