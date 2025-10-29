from aiogram import Router, types
from aiogram.filters import Command
import httpx

from ..config import settings

router = Router(name="me")


@router.message(Command("me"))
async def handle_me(message: types.Message):
    tg_id = message.from_user.id

    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(f"{settings.AUTH_SERVICE_URL}/users/{tg_id}")

    if resp.status_code == 200:
        data = resp.json()
        await message.answer(
            "Твои данные в системе:\n"
            f"ID в базе: {data.get('id')}\n"
            f"telegram_user_id: {data.get('telegram_user_id')}\n"
            f"username: @{data.get('username')}\n"
            f"phone: {data.get('phone')}\n"
            f"is_active: {data.get('is_active')}"
        )
    elif resp.status_code == 404:
        # вот тут ты раньше видел "не зарегистрирован"
        await message.answer(
            "Ты не зарегистрирован 😶\n"
            "Нажми /contact и отправь номер телефона, чтобы создать аккаунт."
        )
    else:
        await message.answer(
            "Сервис авторизации сейчас не отвечает 😔.\n"
            "Попробуй чуть позже."
        )
