import uuid
import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import String, Boolean, DateTime, Enum as SAEnum, BigInteger, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .db_base import Base


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    STANDARD = "standard"
    PREMIUM = "premium"


subscription_enum = SAEnum(
    SubscriptionTier,
    name="subscriptiontier",
    values_callable=lambda cls: [e.value for e in cls],
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    telegram_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    phone_number: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True, index=True)

    subscription_tier: Mapped[SubscriptionTier] = mapped_column(
        subscription_enum,
        nullable=False,
        default=SubscriptionTier.FREE,
    )

    is_subscription_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    subscription_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
