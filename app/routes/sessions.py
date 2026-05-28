from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Session as SessionModel
from app.schemas.session import CreateSessionRequest, SessionResponse, SessionDetailResponse
from app.routes.dependencies import get_current_user
from app.services.session_service import create_session, get_user_sessions, get_session

router = APIRouter()


@router.post("/sessions", response_model=SessionDetailResponse)
async def create_new_session(
    request: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    import uuid
    from app.services.template_service import get_template_by_name

    template = await get_template_by_name(db, request.template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{request.template_id}' not found")

    session_obj = await create_session(db, uuid.UUID(user_id), template.id, request.name)

    return SessionDetailResponse(
        id=session_obj.id,
        name=session_obj.name,
        status=session_obj.status,
        total_images=session_obj.total_images,
        processed_images=session_obj.processed_images,
        created_at=session_obj.created_at,
        updated_at=session_obj.updated_at,
        template_id=session_obj.template_id,
        user_id=session_obj.user_id,
        result_txt_path=session_obj.result_txt_path,
    )


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    import uuid
    sessions = await get_user_sessions(db, uuid.UUID(user_id))
    return sessions


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session_detail(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    import uuid
    session_obj = await get_session(db, uuid.UUID(session_id))
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionDetailResponse(
        id=session_obj.id,
        name=session_obj.name,
        status=session_obj.status,
        total_images=session_obj.total_images,
        processed_images=session_obj.processed_images,
        created_at=session_obj.created_at,
        updated_at=session_obj.updated_at,
        template_id=session_obj.template_id,
        user_id=session_obj.user_id,
        result_txt_path=session_obj.result_txt_path,
    )
