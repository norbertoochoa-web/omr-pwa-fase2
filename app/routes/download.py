from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routes.dependencies import get_current_user
from app.services.session_service import get_session

router = APIRouter()


@router.get("/sessions/{session_id}/download")
async def download_session_txt(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    import uuid
    import os

    session_obj = await get_session(db, uuid.UUID(session_id))
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")

    if session_obj.result_txt_path and os.path.exists(session_obj.result_txt_path):
        file_path = session_obj.result_txt_path
    else:
        from app.services.txt_service import generate_delphi_txt, save_txt_to_file
        from app.config import settings
        txt_content = generate_delphi_txt(session_obj)
        file_path = save_txt_to_file(txt_content, settings.UPLOAD_DIR, str(session_obj.id))
        session_obj.result_txt_path = file_path

    return FileResponse(
        file_path,
        filename=f"{session_obj.id}.txt",
        media_type="application/octet-stream",
    )
