from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Build and return the main reply keyboard used in the bot.

    The keyboard contains a primary action button and a set of popular city
    quick-buttons for convenience.
    """
    # Main menu with Get weather and some popular city quick-buttons
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Get weather")],
            [
                KeyboardButton(text="Tashkent"),
                KeyboardButton(text="Moscow"),
                KeyboardButton(text="London"),
            ],
            [
                KeyboardButton(text="New York"),
                KeyboardButton(text="Tokyo"),
                KeyboardButton(text="Paris"),
            ],
            [KeyboardButton(text="Other city")],
        ],
        resize_keyboard=True,
    )
    return kb
