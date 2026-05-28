from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User
from app.schemas.subscription import SubscriptionResponse
from app.routes.dependencies import get_current_user

router = APIRouter()


@router.get("/subscription/{user_id}", response_model=SubscriptionResponse)
async def get_subscription(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
):
    import uuid

    if user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    expires_str = user.expires.isoformat() if user.expires else None

    return SubscriptionResponse(
        status=user.subscription_status,
        max_images=user.max_images,
        expires=expires_str,
    )
