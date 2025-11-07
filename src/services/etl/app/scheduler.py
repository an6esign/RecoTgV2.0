# services/etl/scheduler.py (минимально)
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from services.etl.app.config import settings
from services.etl.app.app_channels_source import load_channels_from_db
from services.etl.app.pipelines.update_channel_stats_min import update_channel_stats_min
from services.etl.app.utils.ratelimit import human_sleep

engine = create_async_engine(settings.DB_DSN, pool_pre_ping=True, future=True)
Session = async_sessionmaker(engine, expire_on_commit=False)

async def run_daily_from_db(limit_channels: int | None = None, only_active: bool = False):
    async with Session() as s:
        usernames = await load_channels_from_db(s, only_active=only_active, limit=limit_channels)
        for u in usernames:
            try:
                await update_channel_stats_min(s, u)
                print(f"[daily] {u}: done")
            except Exception as e:
                print(f"[daily] {u}: ERROR: {e}")
            await human_sleep(500, 1500)

async def main():
    await run_daily_from_db()

if __name__ == "__main__":
    asyncio.run(main())
