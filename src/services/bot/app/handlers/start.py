from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import httpx

from src.services.bot.app.config import settings
from src.services.bot.app.auth_client import auth_client

router = Router(name="start")

@router.message(CommandStart())
async def handle_start(message: types.Message):
    tg_id = message.from_user.id

    # пробуем найти юзера в auth
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(f"{settings.AUTH_SERVICE_URL}/me/{tg_id}")

    if resp.status_code == 200:
        await message.answer(
            "Вы уже зарегистрированы ✅\n\n"
            "Команды:\n"
            "/me — мой профиль\n"
            "/help — помощь"
        )
        return
    if resp.status_code == 404:
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Поделиться номером", request_contact=True)]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        
        await message.answer(
        "Привет 👋\n"
        "Я RecoTg бот.\n"
        "Я буду рекомендовать тебе лучшие Telegram-каналы.\n\n"
        "Для доступа мне нужно подтвердить твой номер телефона.\n"
        "Нажми на кнопку ниже 👇",
        reply_markup=kb
        )
        return
    
    await message.answer("Сервис временно недоступен. Попробуйте позже 🙏")
    
@router.message(F.contact)
async def got_contact(message: types.Message):
    if not message.contact or message.contact.user_id != message.from_user.id:
        await message.answer("Нужно отправить СВОЙ номер через кнопку «Поделиться номером».")
        return
    
    contact: types.Contact = message.contact
    phone_number = contact.phone_number
    telegram_user_id = message.from_user.id
    
    payload = {
        "phone_number": phone_number,
        "telegram_user_id": telegram_user_id,
    }
    
    async with httpx.AsyncClient(timeout=5) as client:
        resp = await client.post(f"{settings.AUTH_SERVICE_URL}/users", json=payload)

    if resp.status_code in (200, 201):
        await message.answer("Готово! Аккаунт создан ✅\nПосмотреть профиль: /me")
    else:
        await message.answer(f"Не удалось сохранить данные ({resp.status_code}). Попробуйте позже.")
