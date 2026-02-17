import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, Update

from core.logger import logger


class ThrottleMiddleware(BaseMiddleware):
    """Simple in-memory per-user throttling middleware.

    The middleware tracks the last request time per Telegram user and blocks
    subsequent requests that arrive sooner than `rate` seconds. It supports
    `Update`, `Message`, and `CallbackQuery` objects and will attempt to send
    a short notice to the user when throttled.

    Note: this is an in-memory limiter and will not be shared between
    multiple process instances.
    """

    def __init__(self, rate: float = 1.0):
        super().__init__()
        self.rate = float(rate)
        self._last: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Apply throttling to the incoming `event` and call `handler`.

        If the event is received too quickly from the same user, a short
        informational message is sent and the handler is not invoked.
        """
        # Support Update objects (when registered via dp.update.middleware)
        user_id = None
        reply_coro = None

        # If event is Update, extract inner message/callback
        if isinstance(event, Update):
            if event.message and event.message.from_user:
                user_id = event.message.from_user.id
                reply_coro = lambda text: event.message.reply(text)
            elif event.callback_query and event.callback_query.from_user:
                cq = event.callback_query
                user_id = cq.from_user.id

                async def _answer(text: str):
                    try:
                        await cq.answer(text, show_alert=False)
                    except Exception:
                        if cq.message:
                            await cq.message.reply(text)

                reply_coro = _answer
        else:
            # Direct Message or CallbackQuery passed into middleware
            if isinstance(event, Message) and event.from_user:
                user_id = event.from_user.id
                reply_coro = lambda text: event.reply(text)
            elif isinstance(event, CallbackQuery) and event.from_user:
                cq = event

                async def _answer(text: str):
                    try:
                        await cq.answer(text, show_alert=False)
                    except Exception:
                        if cq.message:
                            await cq.message.reply(text)

                reply_coro = _answer

        if user_id is not None:
            now = time.monotonic()
            last = self._last.get(user_id)
            if last is not None and (now - last) < self.rate:
                # Too fast — ignore and optionally inform user
                logger.info("Throttled user {user} — {dt:.3f}s since last", user=user_id, dt=(now - last))
                if reply_coro is not None:
                    try:
                        await reply_coro("Please avoid spamming — try again in a few seconds.")
                    except Exception:
                        logger.exception("Failed to send throttle notice")
                return

            self._last[user_id] = now

        return await handler(event, data)
