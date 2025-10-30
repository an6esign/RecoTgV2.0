from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User  # важно: проверь путь и имя модели
from .schemas import TelegramRegisterRequest, UserPublic, TokenPair
from .tokens import create_token_pair


async def register_or_login_via_telegram(
    db: AsyncSession,
    payload: TelegramRegisterRequest,
) -> tuple[User, TokenPair]:
    """
    Логика:
    - ищем пользователя по telegram_user_id
    - если нет — создаём с phone_number
    - возвращаем (user, token_pair)
    """
    telegram_user_id = payload.telegram_user_id
    phone_number = payload.phone_number

    # 1. ищем
    result = await db.execute(
        select(User).where(User.telegram_user_id == telegram_user_id)
    )
    user = result.scalar_one_or_none()

    # 2. если нет — создаём
    if user is None:
        user = User(
            telegram_user_id=telegram_user_id,
            phone_number=phone_number,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # 3. генерим токены
    tokens = create_token_pair(user_id=user.id)

    return user, tokens


async def get_user_public_by_telegram_id(db: AsyncSession, telegram_user_id: int) -> UserPublic | None:
    result = await db.execute(
        select(User).where(User.telegram_user_id == telegram_user_id)
    )
    user: User | None = result.scalar_one_or_none()
    if user is None:
        return None

    # ВАЖНО: валидируем напрямую из ORM — здесь точно будут ВСЕ поля, включая is_active
    return UserPublic.model_validate(user)