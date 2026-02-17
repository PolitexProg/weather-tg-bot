import json
from pathlib import Path

from core.logger import logger

DEFAULT_FILE_PATH = Path(__file__).parent / "coords.json"


def get_city_coords(city_name: str, filepath: Path = DEFAULT_FILE_PATH) -> dict | None:
    """Return coordinates for a given city name.

    Args:
        city_name: The city name to look up (case-sensitive exact match).
        filepath: Path to the JSON file containing a `coords` mapping.

    Returns:
        A dict with keys `lat` and `lon` or `None` if not found or file is invalid.
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
            return data.get("coords", {}).get(city_name)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


if __name__ == "__main__":
    city = "Moscow"
    coords = get_city_coords(city)

    if coords:
        logger.info("Latitude: {lat}, Longitude: {lon}", lat=coords['lat'], lon=coords['lon'])
    else:
        logger.info("City not found.")
