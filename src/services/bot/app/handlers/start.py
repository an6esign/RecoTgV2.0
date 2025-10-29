from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router(name="start")

WELCOME_TEXT = (
    "Привет 👋\n\n"
    "Я RecoTg бот.\n"
    "Я буду рекомендовать тебе лучшие Telegram-каналы.\n\n"
    "Для доступа мне нужно подтвердить твой номер телефона.\n"
    "Нажми на кнопку ниже 👇"
)

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [KeyboardButton(text="Поделиться номером", request_contact=True)]
    ]

    markup = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await message.answer(WELCOME_TEXT, reply_markup=markup)
