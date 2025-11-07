import asyncio
from typing import Optional, Any
from telethon import TelegramClient
from ..config import settings

_client: Optional[TelegramClient] = None
_lock = asyncio.Lock()
_entity_cache: dict[Any, Any] = {}

async def get_client() -> TelegramClient:
    """Ленивый singleton клиента. Требует заранее авторизованную сессию."""
    global _client
    if _client and _client.is_connected():
        return _client
    async with _lock:
        if _client and _client.is_connected():
            return _client
        _client = TelegramClient(settings.TG_SESSION, settings.TG_API_ID, settings.TG_API_HASH)
        await _client.connect()
        if not await _client.is_user_authorized():
            raise RuntimeError(
                "Telethon session is not authorized. Run: python -m services.etl.auth_session"
            )
        return _client

async def get_entity_cached(ref):
    if ref in _entity_cache:
        return _entity_cache[ref]
    client = await get_client()
    ent = await client.get_entity(ref)
    _entity_cache[ref] = ent
    return ent
