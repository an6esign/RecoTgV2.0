from pydantic import BaseModel, Field
from typing import Optional, Annotated
from pydantic import StringConstraints

Username = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=255)]

class ChannelBase(BaseModel):
    channel: Optional[str] = Field(None, description="@username или https://t.me/username")
    name: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    category: Optional[str] = None
    country: Optional[str] = None
    subscribers: Optional[int] = Field(0, ge=0)

class ChannelCreate(ChannelBase):
    username: Username

class ChannelRead(ChannelBase):
    username: str

class BulkUpsertReport(BaseModel):
    total_rows: int
    inserted: int
    updated: int
    skipped: int
    errors: int
    sample_errors: list[str] = []

# ⬇️ новый тип ответа для одиночного upsert
class ChannelUpsertResponse(BaseModel):
    message: str
    channel: ChannelRead
