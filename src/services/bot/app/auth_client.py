import httpx
from .config import settings

class AuthClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def create_user(self, telegram_user_id: int, phone_number: str | None) -> httpx.Response:
        """
        Регистрация пользователя в auth-сервисе.
        POST /telegram
        body: { telegram_user_id, phone_number }
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            return await client.post(
                f"{self.base_url}/telegram",
                json={
                    "telegram_user_id": telegram_user_id,
                    "phone_number": phone_number,
                },
            )

    async def get_user_info(self, telegram_user_id: int) -> httpx.Response:
        """
        Получение инфы о пользователе (phone_number, subscription_tier, subscription_expires_at)
        GET /me/{telegram_user_id}
        """
        async with httpx.AsyncClient(timeout=5.0) as client:
            return await client.get(f"{self.base_url}/me/{telegram_user_id}")

auth_client = AuthClient(settings.AUTH_SERVICE_URL)
