"""Auth — single-user only."""

from __future__ import annotations

from farzana.core.config import Settings


def is_allowed_user(user_id: int | None, settings: Settings) -> bool:
    """Only TELEGRAM_USER_ID (the owner) may use this bot."""
    if user_id is None:
        return False
    owner = settings.owner_user_id
    if not owner:
        # Misconfigured: refuse everyone rather than open the bot
        return False
    return int(user_id) == int(owner)
