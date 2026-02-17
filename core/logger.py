from __future__ import annotations

import logging
import sys
from pathlib import Path

from loguru import logger

# Ensure logs directory exists
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


# Remove default handler
logger.remove()

# Console handler with custom format
console_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)
logger.add(sys.stderr, format=console_format, level="INFO")

# File handlers
logger.add(
    str(LOG_DIR / "app.log"),
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    enqueue=True,
)
logger.add(
    str(LOG_DIR / "errors.log"),
    level="ERROR",
    rotation="10 MB",
    retention="30 days",
    enqueue=True,
)


class InterceptHandler(logging.Handler):
    """Default handler to intercept standard logging and redirect to loguru."""

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - simple forwarder
        try:
            level = logger.level(record.levelname).name
        except Exception:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


# Replace handlers for stdlib logging
logging.root.handlers = [InterceptHandler()]
logging.basicConfig(handlers=[InterceptHandler()], level=0)

# Optionally silence noisy libraries by setting their level to WARNING and propagate to intercept
for name in ("asyncio", "httpx", "aiogram"):
    logging.getLogger(name).handlers = [InterceptHandler()]
    logging.getLogger(name).setLevel(logging.WARNING)


__all__ = ("logger", "InterceptHandler")
