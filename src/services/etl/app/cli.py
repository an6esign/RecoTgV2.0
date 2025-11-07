# src/services/etl/app/cli.py
import argparse, asyncio
from typing import Optional
from services.etl.app.pipelines.backfill_posts_min import backfill_posts_min
from services.etl.app.pipelines.update_channel_stats_min import update_channel_stats_min
from services.etl.app.app_channels_source import load_channels_from_db
from services.etl.app.utils.ratelimit import human_sleep
from .config import settings
from .db import SessionLocal
from .pipelines.backfill_posts_min import backfill_posts_min
from .pipelines.update_channel_stats_min import update_channel_stats_min

async def cmd_backfill(username: str, limit: int):
    username = username.lstrip("@")
    async with SessionLocal() as s:
        n = await backfill_posts_min(s, username, limit)
        print(f"✅ Backfilled {n} posts for @{username}")

async def cmd_update(username: str):
    username = username.lstrip("@")
    async with SessionLocal() as s:
        await update_channel_stats_min(s, username)
        print(f"✅ Updated channel_stats for @{username}")

async def cmd_backfill_db(limit_posts: int, limit_channels: Optional[int], only_active: bool):
    async with SessionLocal() as s:
        usernames = await load_channels_from_db(s, only_active=only_active, limit=limit_channels)
        for u in usernames:
            try:
                n = await backfill_posts_min(s, u, limit_posts)
                print(f"[backfill] {u}: +{n} posts")
            except Exception as e:
                print(f"[backfill] {u}: ERROR: {e}")
            await human_sleep(400, 1200)

async def cmd_update_db(limit_channels: Optional[int], only_active: bool):
    async with SessionLocal() as s:
        usernames = await load_channels_from_db(s, only_active=only_active, limit=limit_channels)
        for u in usernames:
            try:
                await update_channel_stats_min(s, u)
                print(f"[update] {u}: done")
            except Exception as e:
                print(f"[update] {u}: ERROR: {e}")
            await human_sleep(500, 1500)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="etl")
    sub = p.add_subparsers(dest="cmd")

    p1 = sub.add_parser("backfill")
    p1.add_argument("--username", required=True)
    p1.add_argument("--limit", type=int, default=300)

    p2 = sub.add_parser("update")
    p2.add_argument("--username", required=True)

    p3 = sub.add_parser("backfill-db")
    p3.add_argument("--limit-posts", type=int, default=300, help="сколько постов на канал")
    p3.add_argument("--limit-channels", type=int, default=None, help="сколько каналов обработать за прогон")
    p3.add_argument("--only-active", action="store_true", help="если есть поле is_active в channels")

    p4 = sub.add_parser("update-db")
    p4.add_argument("--limit-channels", type=int, default=None)
    p4.add_argument("--only-active", action="store_true")

    return p


def main():
    p = build_parser()
    args = p.parse_args()

    if args.cmd == "backfill":
        asyncio.run(cmd_backfill(args.username, args.limit))
    elif args.cmd == "update":
        asyncio.run(cmd_update(args.username))
    elif args.cmd == "backfill-db":
        asyncio.run(cmd_backfill_db(args.limit_posts, args.limit_channels, args.only_active))
    elif args.cmd == "update-db":
        asyncio.run(cmd_update_db(args.limit_channels, args.only_active))
    else:
        p.print_help()
