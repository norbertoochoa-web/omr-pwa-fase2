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

    if not session_obj.result_txt_path or not os.path.exists(session_obj.result_txt_path):
        raise HTTPException(status_code=404, detail="Result file not available yet")

    return FileResponse(
        session_obj.result_txt_path,
        filename=f"session_{session_id}_results.txt",
        media_type="text/plain",
    )
