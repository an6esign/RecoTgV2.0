from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_db
from ..schemas import TelegramRegisterRequest, UserPublic, TokenPair, RefreshRequest
from ..service import register_or_login_via_telegram
from ..tokens import create_token_pair, decode_refresh
from ..deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/telegram", response_model=TokenPair)
async def telegram_register(
    payload: TelegramRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    user, tokens = await register_or_login_via_telegram(db, payload)
    return tokens

@router.post("/me", response_model=UserPublic)
async def me(current_user=Depends(get_current_user)):
    return current_user

@router.post("/refresh", response_model=TokenPair)
async def refresh_tokens(body: RefreshRequest):
    try:
        user_id = decode_refresh(body.refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    tokens = create_token_pair(user_id=user_id)
    return tokens
