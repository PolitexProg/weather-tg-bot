from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

POPULAR_CITIES = [
    "Tashkent",
    "Moscow",
    "London",
    "New York",
    "Tokyo",
    "Paris",
    "Dubai",
]


def make_city_keyboard() -> ReplyKeyboardMarkup:
    """Return a reply keyboard populated with popular city choices.

    The keyboard contains one button per popular city and additional
    'Other city' and 'Cancel' actions.
    """
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=c)] for c in POPULAR_CITIES]
        + [[KeyboardButton(text="Other city")], [KeyboardButton(text="Cancel"),]],
        resize_keyboard=True,
    )
    return kb


city_keyboard = make_city_keyboard()
