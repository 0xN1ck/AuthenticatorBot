from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from tgbot.keyboards.reply import generate_market_menu_user
from infrastructure.database.repo.requests import RequestsRepo

import re
import pyotp
import time

user_router = Router()


@user_router.message(CommandStart())
async def user_start(message: Message, repo: RequestsRepo):
    menu = await generate_market_menu_user(await repo.markets.get_all_markets())
    await message.reply("Привет, обычный пользователь!", reply_markup=menu)


@user_router.message(lambda message: re.match(r"📈\u200B", message.text))
async def handle_market_button(message: Message, repo: RequestsRepo):
    market_name = message.text.split("\u200B")[1].strip()
    market_key = await repo.markets.get_market_by_name(market_name)

    if market_key:
        totp = pyotp.TOTP(market_key.market_key)
        generated_otp = totp.now()

        time_remaining = totp.interval - (int(time.time()) % totp.interval)

        await message.reply(f"<i>Вы выбрали ключ:</i> <b>{market_name}</b>\n"
                            f"<i>Одноразовый пароль:</i> <code>{generated_otp}</code>\n"
                            f"<i>Осталось времени:</i> <b>{time_remaining}</b> секунд")
    else:
        await message.reply(f"Не удалось получить секретный ключ для рынка: {market_name}\n"
                            f"<b>Попробуйте выполнить команду /start</b>")

