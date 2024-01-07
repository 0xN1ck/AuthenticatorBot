from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def generate_market_menu_user(markets):
    """
    Generate a ReplyKeyboardMarkup with buttons for each market.
    :param markets: List of market objects.
    :return: ReplyKeyboardMarkup.
    """
    builder = ReplyKeyboardBuilder()

    buttons = [
        KeyboardButton(
            text=f"📈\u200B{market[0]}",
        )
        for market in sorted(markets)
    ]

    for button in buttons:
        builder.add(button)

    builder.adjust(2)

    menu = builder.as_markup(resize_keyboard=True)

    return menu


async def generate_admin_menu():
    buttons = [
        KeyboardButton(text="➕\u200BДобавить"),
        KeyboardButton(text="➖\u200BУдалить"),
        KeyboardButton(text="👁️\u200BПросмотр"),
    ]
    menu = ReplyKeyboardMarkup(keyboard=[buttons], resize_keyboard=True)
    return menu
