# ⛅ Telegram Weather Bot (tg-prognoz)

A fast, async Telegram bot built with **aiogram v3** for weather forecasts and user profile management.

## ⚡ Features

- **Weather:** Fetch current weather via the Open-Meteo API.
- **Profiles:** Create and edit user profiles (Name, City, Hobbies, Age) using inline keyboards.
- **Clean UI:** Step-by-step FSM flows with a simple main menu.
- **Under the hood:** Async SQLite (SQLAlchemy), in-memory rate limiting, HTTPX, and structured logging (`loguru`).

## 🛠 Quick Start

**Requirements:** Python 3.11+

1. **Set up the environment and install dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   export BOT_TOKEN="<your-telegram-bot-token>"
   export AI_TOKEN="<your-gemini-api-token>" # Optional: if using AI features
   ```

3. **Run the bot:**
   ```bash
   python bot/start.py
   ```

## 📂 Data & Logs

- **Database:** `db.sqlite3` (auto-generated on startup).
- **Locations:** `bot/utils/coords.json` (city-to-coordinates mapping).
- **Logs:** Automatically saved to `logs/app.log` and `logs/errors.log`.

## 📜 License

MIT License
