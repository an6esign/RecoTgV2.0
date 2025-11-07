from typing import Tuple, Optional, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, SubscriptionTier
from .schemas import TelegramRegisterRequest, UserPublic, TokenPair
from .tokens import create_token_pair


def _normalize_tier(maybe: Any) -> SubscriptionTier:
    if isinstance(maybe, SubscriptionTier):
        return maybe
    if maybe is None:
        return SubscriptionTier.FREE
    try:
        return SubscriptionTier(str(maybe).lower())
    except Exception:
        return SubscriptionTier.FREE


async def register_or_login_via_telegram(
    db: AsyncSession,
    payload: TelegramRegisterRequest,
) -> Tuple[User, TokenPair]:
    telegram_user_id = payload.telegram_user_id
    phone_number = payload.phone_number

    result = await db.execute(select(User).where(User.telegram_user_id == telegram_user_id))
    user: Optional[User] = result.scalar_one_or_none()

    if user is None:
        tier = _normalize_tier(getattr(payload, "subscription_tier", None))

        user = User(
            telegram_user_id=telegram_user_id,
            phone_number=phone_number,
            subscription_tier=tier,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        if phone_number and user.phone_number != phone_number:
            user.phone_number = phone_number
            await db.commit()
            await db.refresh(user)

    tokens = create_token_pair(user_id=user.id)

    return user, tokens


async def get_user_public_by_telegram_id(db: AsyncSession, telegram_user_id: int) -> Optional[UserPublic]:
    result = await db.execute(select(User).where(User.telegram_user_id == telegram_user_id))
    user: Optional[User] = result.scalar_one_or_none()
    if user is None:
        return None

    return UserPublic.model_validate(user)
