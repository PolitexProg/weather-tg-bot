
# Telegram Weather Bot (tg-prognoz)

A demo Telegram bot for weather and profile management, built with aiogram v3.

## Features

- Main menu: only "Get weather" and "Profile" buttons (no city entry from main menu)
- City selection appears only after clicking "Get weather"
- Profile creation and editing (name, city, hobbies, age) with inline edit button
- Weather fetching using Open-Meteo API
- Async SQLAlchemy (SQLite) for user profiles
- Inline keyboard for profile editing
- Structured logging with loguru

## Requirements

- Python 3.11+ (async/typing features)
- Virtual environment, dependencies from `pyproject.toml`

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Configuration

Set your Telegram bot token:

```bash
export BOT_TOKEN="<your-telegram-bot-token>"
```

## Running

```bash
python bot/start.py
```

## Profile Management

- Use the "Profile" button to view or create your profile
- Edit your profile with the inline "Edit Profile" button
- Profile fields: name, city, hobbies, age

## License

See LICENSE for details (default: MIT).

## Data files

- `bot/utils/coords.json` — city coordinates
- `db.sqlite3` — SQLite DB

## Features

- Reply keyboard with quick city buttons and a "Get weather" flow
- FSM-based city/source selection
- Weather fetching using the Open-Meteo API
- Async HTTP client via `httpx`
- Simple in-memory per-user throttling middleware
- Async SQLAlchemy session middleware (SQLite)
- Structured logging using `loguru` (logs written to `logs/app.log` and `logs/errors.log`)

## Requirements

- Python 3.11+ (project used modern typing and async features)
- A virtual environment with dependencies from `pyproject.toml` / your chosen method

Install dependencies (example using pip):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

(If this project uses `pyproject.toml`, use `pip install -e .` or your preferred tool.)

## Configuration

Set your bot token in the environment before running:

```bash
export BOT_TOKEN="<your-telegram-bot-token>"
```

## Running the bot

Start the bot:

```bash
python bot/start.py
```

Logs are written to `logs/app.log` and errors to `logs/errors.log` (configured in `core/logger.py`).

## Middleware

- `DbSessionMiddleware` (in `bot/middlewares/session.py`): creates an async SQLAlchemy session per update and injects it into handler `data` under the key `session`.
- `ThrottleMiddleware` (in `bot/middlewares/throttle.py`): simple in-memory per-user rate limiter. By default it allows one request per user per second (configured with `rate=1.0` in `bot/start.py`). It supports messages, callback queries and `Update` objects. When a user is throttled, they receive a short informational message.

Notes:
- This throttler is in-memory and does not synchronize across multiple processes. For distributed deployments use Redis or another centralized rate limiter.

## Data files

- `bot/utils/coords.json` — a small mapping of city names to coordinates used by the demo.
- `db.sqlite3` — SQLite DB used by SQLAlchemy (created automatically by the app when running `proceed_schemas()`).

## Development notes

- Main entrypoint: `bot/start.py`
- Handlers: `bot/handlers/` (common handlers and source handlers)
- Services: `bot/services/weather/get_data.py`
- Keyboards: `bot/keyboards/`
- Middlewares: `bot/middlewares/`
- States: `bot/states/`
- Logging configured in `core/logger.py` using `loguru` (logs to `logs/app.log` and `logs/errors.log`)
