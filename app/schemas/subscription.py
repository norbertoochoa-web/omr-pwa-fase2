from pydantic import BaseModel


class SubscriptionResponse(BaseModel):
    status: str
    max_images: int
    expires: str | None = None
