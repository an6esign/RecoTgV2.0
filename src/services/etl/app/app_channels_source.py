# services/etl/app_channels_source.py
from typing import Iterable, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# импортируй свою модель Channel (у тебя она уже есть, раз есть relationship в ChannelStat)
from .models.channel import Channel  # подстрой путь импорта

async def load_channels_from_db(
    session: AsyncSession,
    *,
    only_with_username: bool = True,
    only_active: bool = False,
    limit: Optional[int] = None,
) -> list[str]:
    q = select(Channel.username)

    if only_with_username:
        q = q.where(Channel.username.is_not(None))

    # если у тебя есть флаг в таблице, например Channel.is_active
    if only_active and hasattr(Channel, "is_active"):
        q = q.where(Channel.is_active.is_(True))

    q = q.order_by(Channel.username.asc())
    if limit:
        q = q.limit(limit)

    rows = (await session.execute(q)).scalars().all()
    # убрать пустые/дубликаты, привести к str
    seen, result = set(), []
    for u in rows:
        if not u:
            continue
        u = u.strip()
        if u and u not in seen:
            seen.add(u)
            result.append(u)
    return result
