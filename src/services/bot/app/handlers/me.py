from aiogram import Router, types
from aiogram.filters import Command

from src.services.bot.app.auth_client import auth_client

router = Router(name="me")


@router.message(Command("me"))
async def handle_me(message: types.Message):
    tg_id = message.from_user.id

    resp = await auth_client.get_user_info(tg_id)

    if resp.status_code == 200:
        data = resp.json()

        phone_number = data.get("phone_number") or data.get("phone")
        subscription_tier = data.get("subscription_tier")
        subscription_expires_at = data.get("subscription_expires_at")

        text_lines = [
            "Твои данные в системе:",
            f"📞 Номер: {phone_number}",
            f"💳 Тариф: {subscription_tier}",
            f"⏳ Оплачено до: {subscription_expires_at}",
        ]

        await message.answer("\n".join(text_lines))

    elif resp.status_code == 404:
        # пользователь не зарегистрирован
        await message.answer(
            "Ты не зарегистрирован 😶\n"
            "Нажми /reg и отправь номер телефона, чтобы создать аккаунт."
        )

    else:
        # любая другая ошибка от сервиса
        await message.answer(
            "Сервис авторизации сейчас не отвечает 😔.\n"
            "Попробуй позже."
        )
