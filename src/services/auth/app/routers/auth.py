from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..schemas import (
    TelegramRegisterRequest,
    UserPublic,
    TokenPair,
    RefreshRequest,
)
from ..service import register_or_login_via_telegram, get_user_public_by_telegram_id
from ..tokens import create_token_pair, decode_refresh

router = APIRouter(tags=["auth"])

@router.post("/users", response_model=TokenPair)
async def telegram_register(
    payload: TelegramRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Регистрация/логин через телеграм.
    Возвращает access/refresh токены.
    """
    user, tokens = await register_or_login_via_telegram(db, payload)
    return tokens


@router.get("/me/{telegram_user_id}", response_model=UserPublic)
async def get_me(telegram_user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user_public_by_telegram_id(db, telegram_user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

