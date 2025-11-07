from __future__ import annotations

from datetime import datetime, timedelta, date
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from ..models.channel import Channel, ChannelStat
from ..models.post import Post


def _utc_today() -> date:
    """Возвращает сегодняшнюю дату в UTC без времени."""
    return datetime.utcnow().date()


async def _nearest_stat_on_or_before(sess: AsyncSession, username: str, target_day: date) -> ChannelStat | None:
    """
    Возвращает самую свежую запись channel_stats для @username с датой <= target_day.
    """
    q = (
        select(ChannelStat)
        .where(
            ChannelStat.username == username,
            ChannelStat.date <= target_day,
        )
        .order_by(ChannelStat.date.desc())
        .limit(1)
    )
    return await sess.scalar(q)


async def update_channel_stats_min(session: AsyncSession, username: str) -> None:
    """
    Обновляет (upsert) дневную сводку по каналу в channel_stats на сегодняшнюю дату (UTC).
    """
    username = username.lstrip("@")
    today = _utc_today()
    now = datetime.utcnow()

    # 1️⃣ Получаем канал
    ch: Channel | None = await session.scalar(select(Channel).where(Channel.username == username))
    if not ch:
        print(f"⚠️  Channel @{username} not found in DB")
        return

    # 2️⃣ Временные окна
    dt_24 = now - timedelta(days=1)
    dt_7d = now - timedelta(days=7)
    dt_30d = now - timedelta(days=30)

    # 3️⃣ Подсчёты по окнам
    posts_total = await session.scalar(
        select(func.count()).select_from(Post).where(Post.username == username)
    )

    def _count_since(dt_from: datetime):
        return select(func.count()).select_from(Post).where(
            and_(Post.username == username, Post.posted_at >= dt_from)
        )

    posts_day = await session.scalar(_count_since(dt_24))
    posts_week = await session.scalar(_count_since(dt_7d))
    posts_month = await session.scalar(_count_since(dt_30d))

    # агрегаты по последним 24ч
    agg_24 = await session.execute(
        select(
            func.avg(Post.views_now),     # avg_views_24h
            func.sum(Post.forwards_now),  # forwards
            func.sum(Post.replies_now),   # comments
            func.sum(Post.reactions_now), # reactions
        ).where(and_(Post.username == username, Post.posted_at >= dt_24))
    )
    avg_views_24h, forwards_24, comments_24, reactions_24 = agg_24.one_or_none() or (None, None, None, None)

    # 4️⃣ Подтягиваем предыдущие записи для расчёта дельт
    subs_now = ch.subscribers

    prev_day = await _nearest_stat_on_or_before(session, username, today - timedelta(days=1))
    prev_week = await _nearest_stat_on_or_before(session, username, today - timedelta(days=7))
    prev_month = await _nearest_stat_on_or_before(session, username, today - timedelta(days=30))

    def _delta(cur: int | None, prev: ChannelStat | None) -> int | None:
        if cur is None or prev is None or prev.subscribers is None:
            return None
        return cur - prev.subscribers

    subscribers_day_delta = _delta(subs_now, prev_day)
    subscribers_week_delta = _delta(subs_now, prev_week)
    subscribers_month_delta = _delta(subs_now, prev_month)

    # 5️⃣ Помощник для безопасного int()
    def i(x):  # int or None
        try:
            return int(x) if x is not None else None
        except (TypeError, ValueError):
            return None

    # 6️⃣ Формируем UPSERT (без func.*)
    ins = pg_insert(ChannelStat.__table__).values(
        username=username,
        date=today,

        subscribers=subs_now,
        subscribers_day_delta=subscribers_day_delta,
        subscribers_week_delta=subscribers_week_delta,
        subscribers_month_delta=subscribers_month_delta,

        avg_views_24h=i(avg_views_24h),
        forwards=i(forwards_24),
        comments=i(comments_24),
        reactions=i(reactions_24),

        posts_total=i(posts_total),
        posts_day=i(posts_day),
        posts_week=i(posts_week),
        posts_month=i(posts_month),

        collected_at=now,
    ).on_conflict_do_update(
        index_elements=["username", "date"],
        set_={
            "subscribers": subs_now,
            "subscribers_day_delta": subscribers_day_delta,
            "subscribers_week_delta": subscribers_week_delta,
            "subscribers_month_delta": subscribers_month_delta,
            "avg_views_24h": i(avg_views_24h),
            "forwards": i(forwards_24),
            "comments": i(comments_24),
            "reactions": i(reactions_24),
            "posts_total": i(posts_total),
            "posts_day": i(posts_day),
            "posts_week": i(posts_week),
            "posts_month": i(posts_month),
            "collected_at": now,  # только Python datetime
        },
    )

    await session.execute(ins)
    await session.commit()
    print(f"✅ Updated channel_stats for @{username} ({today})")
