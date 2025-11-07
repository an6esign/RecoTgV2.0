import asyncio
from telethon import TelegramClient
from .config import settings

async def main():
    client = TelegramClient(settings.TG_SESSION, settings.TG_API_ID, settings.TG_API_HASH)
    await client.start(
        phone=lambda: input("Your phone (+17244123125): "),
        code_callback=lambda: input("Telegram code: "),
        password=lambda: input("2FA password (if any): ")  # если включена
    )
    print(f"Session saved to {settings.TG_SESSION}")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
