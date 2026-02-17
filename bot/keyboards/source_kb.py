from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def make_source_keyboard() -> ReplyKeyboardMarkup:
    """Return a simple keyboard allowing the user to pick a weather source.

    Currently this contains a placeholder option and a 'Cancel' action.
    """
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Open-Meteo")],
            [KeyboardButton(text="Other (placeholder)")],
            [KeyboardButton(text="Cancel")],
        ],
        resize_keyboard=True,
    )
    return kb

source_keyboard = make_source_keyboard()
