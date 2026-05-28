from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Session as SessionModel
from app.schemas.session import CreateSessionRequest, CreateSessionResponse, SessionResponse, FinishSessionResponse
from app.routes.dependencies import get_current_user
from app.services.session_service import create_session, get_user_sessions, get_session, finish_session
from app.services.email_service import send_session_email
from app.services.txt_service import generate_delphi_txt, save_txt_to_file
from app.config import settings

router = APIRouter()


@router.post("/sessions", response_model=CreateSessionResponse, status_code=201)
async def create_new_session(
    request: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    import uuid
    session_obj = await create_session(db, uuid.UUID(user_id), request.name)
    return CreateSessionResponse(
        session_token=str(session_obj.id),
        status=session_obj.status,
    )


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    import uuid
    sessions = await get_user_sessions(db, uuid.UUID(user_id))
    return [
        SessionResponse(
            id=str(s.id),
            name=s.name,
            status=s.status,
            total_images=s.total_images,
            processed_images=s.processed_images,
            created_at=s.created_at,
            updated_at=s.updated_at,
            email_sent=s.email_sent,
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session_detail(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    import uuid
    session_obj = await get_session(db, uuid.UUID(session_id))
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse(
        id=str(session_obj.id),
        name=session_obj.name,
        status=session_obj.status,
        total_images=session_obj.total_images,
        processed_images=session_obj.processed_images,
        created_at=session_obj.created_at,
        updated_at=session_obj.updated_at,
        email_sent=session_obj.email_sent,
    )


@router.post("/sessions/{session_id}/finish", response_model=FinishSessionResponse)
async def finish_session_endpoint(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
):
    import uuid
    from sqlalchemy import select
    from app.models import User

    session_obj = await get_session(db, uuid.UUID(session_id))
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")

    await finish_session(db, uuid.UUID(session_id))

    txt_content = generate_delphi_txt(session_obj)
    txt_path = save_txt_to_file(txt_content, settings.UPLOAD_DIR, str(session_obj.id))
    session_obj.result_txt_path = txt_path

    emailed = False
    result = await db.execute(select(User).where(User.id == session_obj.user_id))
    user = result.scalar_one_or_none()
    if user:
        emailed = await send_session_email(session_obj, user.email)

    await db.flush()

    return FinishSessionResponse(
        status="COMPLETED",
        emailed=emailed,
        txt_filename=f"{session_obj.id}.txt",
    )
