from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas.auth import LoginRequest, LoginResponse, SubscriptionObject
from app.services.auth_service import authenticate_user, create_token

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
