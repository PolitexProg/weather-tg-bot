from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def edit_profile_keyboard() -> InlineKeyboardMarkup:
    """Return an inline keyboard for profile management.

    The keyboard contains buttons for editing the profile
    """
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Edit Profile", callback_data="edit_profile")],
        ]
    )
    return kb
