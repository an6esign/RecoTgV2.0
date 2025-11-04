from __future__ import annotations
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.channel import Channel, ChannelStat

class ChannelConflictError(Exception):
    def __init__(self, channel: str, existing_username: str):
        super().__init__(f"channel '{channel}' belongs to '{existing_username}'")
        self.channel = channel
        self.existing_username = existing_username

# ➜ теперь возвращаем (obj, created: bool)
async def upsert_channel(db: AsyncSession, payload: dict) -> Tuple[Channel, bool]:
    username = payload["username"]
    new_channel = payload.get("channel")

    # существующий по username
    obj: Optional[Channel] = await db.scalar(select(Channel).where(Channel.username == username))
    if obj:
        # проверим, что новый channel не занят другим пользователем
        if new_channel:
            taken_by = await db.scalar(
                select(Channel.username).where(
                    Channel.channel == new_channel, Channel.username != username
                )
            )
            if taken_by:
                raise ChannelConflictError(new_channel, taken_by)
        for k, v in payload.items():
            if k == "username":
                continue
            if v is not None:
                setattr(obj, k, v)
        await db.flush()
        return obj, False  # updated

    # вставка: убедимся, что channel не занят
    if new_channel:
        existing = await db.scalar(select(Channel).where(Channel.channel == new_channel))
        if existing:
            raise ChannelConflictError(new_channel, existing.username)

    obj = Channel(**payload)
    db.add(obj)
    await db.flush()
    return obj, True  # created
