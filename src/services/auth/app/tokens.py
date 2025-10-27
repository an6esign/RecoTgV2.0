import jwt
import os
from datetime import datetime, timedelta

ALGORITHM = "HS256"

# читаем из окружения (которое docker-compose пробросит из .env)
JWT_ACCESS_SECRET = os.getenv("JWT_ACCESS_SECRET", "dev_access_secret_fallback")
JWT_REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET", "dev_refresh_secret_fallback")

ACCESS_TTL_MINUTES = int(os.getenv("ACCESS_TTL_MINUTES", "15"))
REFRESH_TTL_DAYS = int(os.getenv("REFRESH_TTL_DAYS", "30"))


def _encode(payload: dict, secret: str, ttl: timedelta) -> str:
    to_encode = payload.copy()
    now = datetime.utcnow()
    to_encode["iat"] = now
    to_encode["exp"] = now + ttl
    token = jwt.encode(to_encode, secret, algorithm=ALGORITHM)
    return token

def create_token_pair(user_id: int) -> dict:
    access_token = _encode(
        payload={"sub": str(user_id), "type": "access"},
        secret=JWT_ACCESS_SECRET,
        ttl=timedelta(minutes=ACCESS_TTL_MINUTES),
    )

    refresh_token = _encode(
        payload={"sub": str(user_id), "type": "refresh"},
        secret=JWT_REFRESH_SECRET,
        ttl=timedelta(days=REFRESH_TTL_DAYS),
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
    
def decode_refresh(token: str) -> int:
    data = jwt.decode(token, JWT_REFRESH_SECRET, algorithms=[ALGORITHM])
    if data.get("type") != "refresh":
        raise ValueError("Not a refresh token")
    return int(data["sub"])