import httpx
from .config import settings


class AuthClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def get_user(self, telegram_user_id: int) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            return await client.get(
                f"{self.base_url}/telegram/{telegram_user_id}",
                timeout=10.0,
            )

    async def create_user(
        self,
        telegram_user_id: int,
        phone_number: str | None,
    ) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            return await client.post(
                f"{self.base_url}/telegram",
                json={
                    "telegram_user_id": telegram_user_id,
                    "phone_number": phone_number,
                },
                timeout=10.0,
            )


auth_client = AuthClient(settings.AUTH_SERVICE_URL)
