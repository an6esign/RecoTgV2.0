import asyncio
from telethon import errors

async def safe_call(coro):
    try:
        return await coro
    except errors.FloodWaitError as e:
        await asyncio.sleep(e.seconds + 1)
        return await coro
