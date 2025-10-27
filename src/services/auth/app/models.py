import uuid
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Boolean, DateTime, Enum, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import enum

from src.services.auth.app.db import Base


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    STANDARD = "standard"
    PREMIUM = "premium"


class User(Base):
    __tablename__ = "users"

    # Уникальный внутренний ID в нашей системе (UUID)
    id: Mapped[uuid4] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Telegram user id (число). Важно: уникальный.
    telegram_user_id: Mapped[int] = mapped_column(
        BigInteger,        # у телеграма id может быть большой int
        unique=True,
        nullable=False,
        index=True,
    )

    # Номер телефона пользователя (в международном формате, типа +49123456789)
    phone_number: Mapped[str | None] = mapped_column(
        String(length=32),
        unique=True,
        nullable=True,
        index=True,
    )

    # Подписка: free | standard | premium
    subscription_tier: Mapped[SubscriptionTier] = mapped_column(
        Enum(SubscriptionTier, name="subscriptiontier"),
        nullable=False,
        default=SubscriptionTier.FREE,
    )

    # Подписка активна?
    is_subscription_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    # Когда эта подписка истекает
    subscription_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Аккаунт вообще активен (можно ли пользоваться сервисом)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )


    # Аудитные поля
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
