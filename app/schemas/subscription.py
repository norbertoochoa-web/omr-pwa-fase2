import uuid
import datetime
from pydantic import BaseModel


class SubscriptionResponse(BaseModel):
    user_id: uuid.UUID
    subscription_status: str
    is_active: bool
