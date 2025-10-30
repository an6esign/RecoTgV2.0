from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class TelegramRegisterRequest(BaseModel):
    telegram_user_id: int
    phone_number: str

class UserPublic(BaseModel):
    id: UUID
    telegram_user_id: int
    phone_number: Optional[str] = None
    subscription_tier: Optional[str] = None
    is_subscription_active: bool
    subscription_expires_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str
