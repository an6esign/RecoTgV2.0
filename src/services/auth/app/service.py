from typing import Tuple, Optional, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, SubscriptionTier
from .schemas import TelegramRegisterRequest, UserPublic, TokenPair
from .tokens import create_token_pair


def _normalize_tier(maybe: Any) -> SubscriptionTier:
    """
    Приводит вход к SubscriptionTier:
    - SubscriptionTier -> как есть
    - "FREE"/"free"/"Free" -> SubscriptionTier.FREE
    - None/пусто -> SubscriptionTier.FREE (дефолт)
    """
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
    """
    Логика:
    - ищем пользователя по telegram_user_id
    - если нет — создаём (phone_number, subscription_tier=FREE по умолчанию)
    - возвращаем (user, token_pair)
    """
    telegram_user_id = payload.telegram_user_id
    phone_number = payload.phone_number

    # 1. ищем
    result = await db.execute(select(User).where(User.telegram_user_id == telegram_user_id))
    user: Optional[User] = result.scalar_one_or_none()

    # 2. если нет — создаём
    if user is None:
        # если когда-то начнёшь присылать tier в payload — он тоже нормализуется
        tier = _normalize_tier(getattr(payload, "subscription_tier", None))

        user = User(
            telegram_user_id=telegram_user_id,
            phone_number=phone_number,
            subscription_tier=tier,  # гарантированно 'free'|'standard'|'premium'
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        # опционально: обновим телефон, если появился новый
        if phone_number and user.phone_number != phone_number:
            user.phone_number = phone_number
            await db.commit()
            await db.refresh(user)

    # 3. генерим токены
    tokens = create_token_pair(user_id=user.id)

    return user, tokens


async def get_user_public_by_telegram_id(db: AsyncSession, telegram_user_id: int) -> Optional[UserPublic]:
    result = await db.execute(select(User).where(User.telegram_user_id == telegram_user_id))
    user: Optional[User] = result.scalar_one_or_none()
    if user is None:
        return None

    # валидируем напрямую из ORM — тут будут все поля
    return UserPublic.model_validate(user)
