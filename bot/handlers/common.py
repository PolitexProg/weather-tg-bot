import difflib
import json
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.choice_kb import POPULAR_CITIES, city_keyboard
from bot.keyboards.keyboard import get_main_menu_keyboard
from bot.services.weather.get_data import WeatherService, build_weather_message
from bot.states.choice_state import ChoiceState
from bot.utils.get_coords import get_city_coords
from core.logger import logger

"""Common message handlers for the bot: start, weather flow and quick buttons."""

router = Router()


@router.message(CommandStart())
@logger.catch
async def cmd_start(message: Message):
    """Handle the /start command and show the main menu keyboard."""
    await message.answer(
        "Hello! I'm a demo bot providing weather information.",
        reply_markup=get_main_menu_keyboard(),
    )


@router.message(F.text == "Get weather")
@logger.catch
async def cmd_get_weather(message: Message, state: FSMContext):
    """Start the weather selection flow and set FSM to choosing_city."""
    await message.answer(
        "Choose a city from the list or type the city name in English:",
        reply_markup=city_keyboard,
    )
    await state.set_state(ChoiceState.choosing_city)


@router.message(ChoiceState.choosing_city)
@logger.catch
async def process_city(message: Message, state: FSMContext):
    """Process user input when choosing a city.

    The handler performs name lookup (exact and fuzzy), fetches weather via
    `WeatherService` and returns a formatted message back to the user.
    """
    text = (message.text or "").strip()
    if not text:
        await message.answer("Please enter a city name.")
        return

    if text == "Cancel":
        await state.clear()
        await message.answer("Cancelled.", reply_markup=get_main_menu_keyboard())
        return

    if text == "Other city":
        await message.answer("Please enter the city name in English (e.g.: London):")
        return

    # try exact lookup
    coords = get_city_coords(text)
    city_name = text

    if not coords:
        # try case-insensitive direct match and fuzzy suggestions
        coords_file = Path(__file__).resolve().parent.parent / "utils" / "coords.json"
        try:
            data = json.loads(coords_file.read_text(encoding="utf-8"))
            names = list(data.get("coords", {}).keys())
        except Exception:
            names = []

        # case-insensitive exact
        match = next((n for n in names if n.lower() == text.lower()), None)
        if match:
            coords = data["coords"][match]
            city_name = match
        else:
            close = difflib.get_close_matches(text, names, n=3, cutoff=0.6)
            if close:
                await message.answer(
                    f"City '{text}' not found. Did you mean: {', '.join(close)}?\nPlease enter the exact name or choose from the list.",
                    reply_markup=city_keyboard,
                )
                return
            else:
                await message.answer(
                    f"City '{text}' not found. Please try a different name.", reply_markup=city_keyboard
                )
                return

    # fetch weather
    weather_service = WeatherService()
    lat, lon = coords["lat"], coords["lon"]
    report = await weather_service.get_weather(lat, lon)
    await weather_service.close()

    if report:
        header = f"<b>📍 {city_name}</b> — {lat}, {lon}\n\n"
        weather_message = build_weather_message(report)
        await message.answer(header + weather_message, parse_mode="HTML")
    else:
        await message.answer("Failed to retrieve weather data.")

    await state.clear()


@logger.catch
async def _fetch_and_send_weather(message: Message, city_name: str):
    """Helper that looks up coordinates for `city_name` and sends weather.

    This is used by quick-button handlers to avoid duplicating fetch logic.
    """
    coords = get_city_coords(city_name)
    used_name = city_name

    if not coords:
        # try case-insensitive lookup
        coords_file = Path(__file__).resolve().parent.parent / "utils" / "coords.json"
        try:
            data = json.loads(coords_file.read_text(encoding="utf-8"))
            names = list(data.get("coords", {}).keys())
        except Exception:
            names = []

        match = next((n for n in names if n.lower() == city_name.lower()), None)
        if match:
            coords = data["coords"][match]
            used_name = match

    if not coords:
        await message.answer("Coordinates for this city were not found.")
        return

    weather_service = WeatherService()
    lat, lon = coords["lat"], coords["lon"]
    report = await weather_service.get_weather(lat, lon)
    await weather_service.close()

    if report:
        header = f"<b>📍 {used_name}</b> — {lat}, {lon}\n\n"
        weather_message = build_weather_message(report)
        await message.answer(header + weather_message, parse_mode="HTML")
    else:
        await message.answer("Failed to retrieve weather data.")


@router.message(F.text.in_(set(POPULAR_CITIES)))
@logger.catch
async def quick_city_click(message: Message):
    """Handle presses of popular city quick-buttons from the main keyboard."""
    text = (message.text or "").strip()
    await _fetch_and_send_weather(message, text)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Show a short help text listing available commands."""
    await message.answer("Commands:\n/start - start conversation\n/help - show this message")
