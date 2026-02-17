from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.keyboard import get_main_menu_keyboard
from bot.keyboards.source_kb import source_keyboard
from bot.states.choice_state import ChoiceState
from core.logger import logger

router = Router()


@router.message(Command("choose_source"))
@logger.catch
async def cmd_choose_source(message: Message, state: FSMContext):
    """Start a conversation to choose a weather data source.

    Sets FSM state `ChoiceState.choosing_source` and shows the source keyboard.
    """
    await message.answer("Choose a weather data source:", reply_markup=source_keyboard)
    await state.set_state(ChoiceState.choosing_source)


@router.message(ChoiceState.choosing_source)
@logger.catch
async def choose_source(message: Message, state: FSMContext):
    """Handle the user's choice of weather source and persist it in FSM data.

    If the user selects 'Cancel' the flow is aborted and the main menu is shown.
    """
    text = message.text
    if text == "Cancel":
        await message.answer("Cancelled", reply_markup=get_main_menu_keyboard())
        await state.clear()
        return

    # Save selected source into FSM data
    await state.update_data(source=text)
    await message.answer(f"Source selected: {text}", reply_markup=get_main_menu_keyboard())
    await state.clear()
