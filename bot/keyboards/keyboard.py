from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Build and return the main reply keyboard used in the bot.

    The keyboard contains a primary action button and a set of popular city
    quick-buttons for convenience.
    """
    # Main menu with icon-enhanced buttons (no city quick-buttons here)
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌤️ Get weather")],
            [KeyboardButton(text="  Profile")],
        ],
        resize_keyboard=True,
    )
    return kb
