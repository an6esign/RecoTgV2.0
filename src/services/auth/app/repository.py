from uuid import UUID, uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from .models import User
from .schemas import TelegramRegisterRequest

async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_telegram_user_id(db: AsyncSession, telegram_user_id: int) -> User | None:
    result = await db.execute(
        select(User).where(User.telegram_user_id == telegram_user_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_phone(db: AsyncSession, phone_number: str) -> User | None:
    result = await db.execute(
        select(User).where(User.phone_number == phone_number)
    )
    return result.scalar_one_or_none()

async def create_user_from_telegram(db: AsyncSession, payload: TelegramRegisterRequest) -> User:
    user = await get_user_by_telegram_user_id(db, payload.telegram_user_id)
    if user:
        return user

    user = await get_user_by_phone(db, payload.phone_number)
    if user:
        user.telegram_user_id = payload.telegram_user_id
        user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
        return user

    now = datetime.utcnow()

    user = User(
        id=uuid4(),
        telegram_user_id=payload.telegram_user_id,
        phone_number=payload.phone_number,
        subscription_tier="free",
        is_subscription_active=False,
        subscription_expires_at=None, 
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user