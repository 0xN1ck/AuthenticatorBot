from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.filters.callback_data import CallbackData

from tgbot.config import load_config


class MyCallbackData(CallbackData, prefix="my"):
    action: str
    target: str
    user_id: str
    username: str
    market_name: str


async def generate_user_key_menu(action):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text=f"👤 Пользователь",
        callback_data=MyCallbackData(action=action,
                                     target="user",
                                     user_id="",
                                     username="",
                                     market_name="").pack()
    )
    keyboard.button(
        text=f"🔑 Ключ",
        callback_data=MyCallbackData(action=action,
                                     target="key",
                                     user_id="",
                                     username="",
                                     market_name="").pack()
    )

    keyboard.adjust(2)

    return keyboard.as_markup()


async def generate_users_menu(action, target, repo):
    keyboard = InlineKeyboardBuilder()

    all_users = await repo.users.get_all_users()

    for user in all_users:
        user_id = str(user[0].user_id)
        username = user[0].username

        config = load_config("../../.env")
        if int(user_id) in config.tg_bot.admin_ids:
            continue

        keyboard.button(
            text=f"👤 {username}",
            callback_data=MyCallbackData(action=action,
                                         target=target,
                                         user_id=user_id,
                                         username=username,
                                         market_name="").pack()
        )

    keyboard.adjust(1)

    return keyboard.as_markup()


async def generate_keys_menu(action, target, repo):
    keyboard = InlineKeyboardBuilder()

    all_keys = await repo.markets.get_all_markets()

    for key in all_keys:
        market_name = str(key.market_name)
        keyboard.button(
            text=f"🔑 {market_name}",
            callback_data=MyCallbackData(action=action,
                                         target=target,
                                         user_id="",
                                         username="",
                                         market_name=market_name).pack()
        )

    keyboard.adjust(1)

    return keyboard.as_markup()
