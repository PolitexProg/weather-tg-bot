from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker


class DbSessionMiddleware(BaseMiddleware):
    """Middleware that provides an async SQLAlchemy session for each update.

    Injects a session into the handler `data` mapping under the key `'session'`.
    The session is created from the provided `async_sessionmaker` and is
    closed automatically when the handler completes.
    """
    def __init__(self, session_pool: async_sessionmaker):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Open a session, add it to `data`, and call the handler.

        The session is available to handlers via the `data` dict and will be
        committed/closed by the context manager when the handler returns.
        """
        async with self.session_pool() as session:
            data["session"] = session
            return await handler(event, data)
