from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User
from app.schemas.subscription import SubscriptionResponse
from app.routes.dependencies import get_current_user

router = APIRouter()


@router.get("/subscription/{user_id}", response_model=SubscriptionResponse)
async def get_subscription(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return SubscriptionResponse(
        user_id=user.id,
        subscription_status=user.subscription_status,
        is_active=user.subscription_status == "ACTIVE" and user.is_active,
    )
