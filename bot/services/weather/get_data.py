from __future__ import annotations

import asyncio
import time
from datetime import datetime

import httpx
from pydantic import BaseModel

from core.logger import logger


class WeatherReport(BaseModel):
    temperature: float
    windspeed: float
    winddirection: float
    weathercode: int
    time: str
    def format_time(self) -> str:
        """Return a human-readable timestamp for the report's ISO time string."""
        return datetime.fromisoformat(self.time).strftime("%Y-%m-%d %H:%M:%S")

    @property
    def condition(self) -> str:
        """Return a short human-friendly description for the WMO weather code."""
        descriptions = {
            0: "Clear ☀️",
            1: "Mainly clear 🌤",
            2: "Partly cloudy ⛅️",
            3: "Overcast ☁️",
            45: "Fog 🌫",
            48: "Depositing rime fog ❄️",
            51: "Light drizzle 🌧",
            61: "Light rain 🌦",
            71: "Light snowfall 🌨",
            95: "Thunderstorm ⛈",
        }
        return descriptions.get(self.weathercode, f"Code {self.weathercode}")


class WeatherService:
    """Service responsible for fetching current weather from Open-Meteo.

    Features:
    - optional in-memory caching with TTL (default: 60s)
    - simple retry with exponential backoff
    - configurable timeout and number of retries
    """

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(
        self,
        timeout: float = 10.0,
        cache_ttl: int = 60,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ) -> None:
        """Create the weather service.

        Args:
            timeout: HTTP client timeout in seconds.
            cache_ttl: Time-to-live for in-memory cache entries (seconds).
            max_retries: Number of attempts for transient failures.
            backoff_factor: Base backoff multiplier for retries.
        """
        self._client = httpx.AsyncClient(timeout=timeout)
        self._cache_ttl = int(cache_ttl)
        self._cache: dict[tuple[float, float], tuple[float, WeatherReport | None]] = {}
        self._max_retries = int(max_retries)
        self._backoff = float(backoff_factor)

    async def close(self) -> None:
        """Close the underlying HTTP client connection pool."""
        await self._client.aclose()

    def _get_cache(self, lat: float, lon: float) -> WeatherReport | None:
        key = (round(lat, 4), round(lon, 4))
        item = self._cache.get(key)
        if not item:
            return None
        ts, report = item
        if time.monotonic() - ts > self._cache_ttl:
            # expired
            del self._cache[key]
            return None
        return report

    def _set_cache(self, lat: float, lon: float, report: WeatherReport | None) -> None:
        key = (round(lat, 4), round(lon, 4))
        self._cache[key] = (time.monotonic(), report)

    @logger.catch
    async def get_weather(self, lat: float, lon: float) -> WeatherReport | None:
        """Fetch current weather for the specified coordinates with retries and caching.

        Returns a `WeatherReport` on success or `None` on failure.
        """
        # Check cache first
        cached = self._get_cache(lat, lon)
        if cached is not None:
            logger.debug("Weather cache hit for {}, {}", lat, lon)
            return cached

        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "timezone": "auto",
        }

        last_exc: Exception | None = None
        for attempt in range(1, self._max_retries + 1):
            try:
                logger.info("Requesting weather for coordinates: {}, {} (attempt {})", lat, lon, attempt)
                response = await self._client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json().get("current_weather")
                if not data:
                    logger.error("API response missing 'current_weather' field")
                    self._set_cache(lat, lon, None)
                    return None

                report = WeatherReport(**data)
                # store successful response in cache
                self._set_cache(lat, lon, report)
                return report

            except httpx.HTTPStatusError as e:
                last_exc = e
                status = e.response.status_code if e.response is not None else "?"
                logger.warning("API returned HTTP status %s for coords %s,%s", status, lat, lon)
                # For 4xx errors, do not retry
                if 400 <= getattr(e.response, "status_code", 500) < 500:
                    break
            except httpx.RequestError as e:
                last_exc = e
                logger.warning("Request error for %s,%s: %s", lat, lon, e)
            except Exception as e:
                last_exc = e
                logger.exception("Unexpected error while fetching weather for %s,%s", lat, lon)

            # exponential backoff with jitter
            if attempt < self._max_retries:
                backoff = self._backoff * (2 ** (attempt - 1))
                jitter = backoff * 0.1
                wait = backoff + (jitter * (0.5 - asyncio.get_event_loop().time() % 1))
                await asyncio.sleep(max(0.1, wait))

        logger.error("Failed to fetch weather after %s attempts: %s", self._max_retries, last_exc)
        # cache negative result briefly to avoid tight loops
        self._set_cache(lat, lon, None)
        return None


def build_weather_message(report: WeatherReport) -> str:
    """Format a `WeatherReport` into an HTML-safe message string.

    The returned string is intended to be sent with `parse_mode='HTML'.`
    """
    return (
        f"<b>📊 Weather Report</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🌡 Temperature: <b>{report.temperature}°C</b>\n"
        f"☁️ Condition: {report.condition}\n"
        f"💨 Wind: {report.windspeed} km/h ({report.winddirection}°)\n"
        f"🕒 Time (UTC): {report.format_time()}\n"
        f"━━━━━━━━━━━━━━━"
    )
