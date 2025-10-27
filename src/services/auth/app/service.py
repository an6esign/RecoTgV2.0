from sqlalchemy.ext.asyncio import AsyncSession
from . import repository
from .schemas import TelegramRegisterRequest
from .tokens import create_token_pair

async def register_or_login_via_telegram(db: AsyncSession, payload: TelegramRegisterRequest):
    user = await repository.get_user_by_telegram_id(db, payload.telegram_user_id)

    if user is None:
        user = await repository.create_user_from_telegram(db, payload)

    tokens = create_token_pair(user_id=user.id)
    return user, tokens