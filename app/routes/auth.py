from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, Session
from app.schemas.auth import LoginRequest, LoginResponse, SSORequest, SubscriptionObject
from app.services.auth_service import authenticate_user, create_token, decode_token

router = APIRouter()


@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(request.email, request.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_active or user.subscription_status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu suscripción no está activa. Contacta a soporte para renovar.",
            headers={"X-Error-Code": "SUBSCRIPTION_INACTIVE"},
        )

    token = create_token(user.id, user.email)

    expires_str = user.expires.isoformat() if user.expires else None

    return LoginResponse(
        token=token,
        user_id=str(user.id),
        subscription=SubscriptionObject(
            status=user.subscription_status,
            max_images=user.max_images,
            expires=expires_str,
        ),
    )


@router.post("/auth/sso", response_model=LoginResponse)
async def sso_login(request: SSORequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(request.token)
    if not payload or payload.get("type") != "qr_access":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido",
        )

    institution_id = payload.get("institution_id")
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido: sin institución",
        )

    result = await db.execute(
        select(User).join(Session).where(Session.institution_id == institution_id).limit(1)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se encontró un usuario para esta institución",
        )

    if not user.is_active or user.subscription_status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu suscripción no está activa. Contacta a soporte para renovar.",
            headers={"X-Error-Code": "SUBSCRIPTION_INACTIVE"},
        )

    token = create_token(user.id, user.email)
    expires_str = user.expires.isoformat() if user.expires else None

    return LoginResponse(
        token=token,
        user_id=str(user.id),
        subscription=SubscriptionObject(
            status=user.subscription_status,
            max_images=user.max_images,
            expires=expires_str,
        ),
    )
