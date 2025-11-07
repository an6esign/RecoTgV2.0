from __future__ import annotations

from datetime import datetime
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from telethon.tl.types import Channel
from sqlalchemy import select
from ..models.channel import Channel as ChannelModel

# относительные импорты внутри пакета etl.app
from ..clients.telethon_client import get_client
from ..models.post import Post
from ..config import settings

import logging

logger = logging.getLogger(__name__)


async def backfill_posts_min(session: AsyncSession, username: str, limit: int = 300) -> int:

    username = username.lstrip("@")
    logger.info("▶️ Backfill start: @%s (limit=%d)", username, limit)

    client = await get_client()   # ожидается, что get_client сам использует settings.API_ID, settings.API_HASH, settings.tg_session_path
    await client.connect()
    try:
        ent = await client.get_entity(username)
        if not isinstance(ent, Channel):
            logger.warning("⚠️ Entity for @%s is not a Channel (%s)", username, type(ent))
            return 0
        
        exists = await session.scalar(select(ChannelModel.username).where(ChannelModel.username == username))
        if not exists:
            session.add(ChannelModel(username=username, channel=username, name=getattr(ent, "title", username)))
            await session.flush()

        processed = 0
        async for m in client.iter_messages(ent, limit=limit):
            if not getattr(m, "id", None) or not getattr(m, "date", None):
                continue

            views     = getattr(m, "views", None)
            forwards  = getattr(m, "forwards", None)
            replies   = (m.replies.replies if getattr(m, "replies", None) else None)
            reactions = None
            if getattr(m, "reactions", None) and m.reactions.results:
                reactions = sum(r.count for r in m.reactions.results)

            stmt = pg_insert(Post.__table__).values(
                username=username,
                message_id=m.id,
                posted_at=m.date.replace(tzinfo=None),
                text=(m.message or None),
                views_now=views,
                forwards_now=forwards,
                replies_now=replies,
                reactions_now=reactions,
                collected_at=datetime.utcnow(),
            ).on_conflict_do_nothing(index_elements=["username", "message_id"])

            await session.execute(stmt)
            processed += 1

        await session.commit()
        logger.info("✅ Backfill done: @%s — %d messages processed", username, processed)
        return processed
    finally:
        await client.disconnect()
        logger.debug("🔌 Disconnected client for @%s", username)


# ── опциональная точка входа, чтобы модуль можно было запускать напрямую ──
if __name__ == "__main__":
    import argparse
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

    p = argparse.ArgumentParser()
    p.add_argument("--username", required=True)
    p.add_argument("--limit", type=int, default=settings.BACKFILL_LIMIT)
    args = p.parse_args()

    engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)
    SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

    async def _run():
        async with SessionLocal() as s:
            n = await backfill_posts_min(s, args.username, args.limit)
            print(f"ETL DONE: inserted_or_skipped={n} username={args.username} limit={args.limit}")

    asyncio.run(_run())
