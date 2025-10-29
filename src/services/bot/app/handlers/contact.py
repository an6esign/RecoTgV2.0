from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardRemove
from src.services.bot.app.auth_client import auth_client  # импорт готового клиента

router = Router(name="contact")


@router.message(F.contact)
async def got_contact(message: types.Message):
    contact: types.Contact = message.contact

    phone_number = contact.phone_number
    telegram_user_id = message.from_user.id

    # ВАЖНО: вызываем напрямую auth_client.create_user(...), без второго auth_client
    resp = await auth_client.create_user(
        telegram_user_id=telegram_user_id,
        phone_number=phone_number,
    )

    if resp.status_code in (200, 201):
        await message.answer(
            "Готово 🎉 Ты зарегистрирован. Доступ открыт.",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            f"Не получилось сохранить тебя 😢\nКод ошибки сервера: {resp.status_code}",
            reply_markup=ReplyKeyboardRemove(),
        )
