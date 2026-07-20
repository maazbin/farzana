"""Auth / allowlist rules for inbound channel messages."""

from __future__ import annotations

from farzana.core.config import Settings


def is_allowed_user(user_id: int | None, settings: Settings) -> bool:
    """
    - telegram_allow_all_users=true (default) → any Telegram user
    - else only ids in TELEGRAM_ALLOWLIST_USER_IDS
    - empty allowlist + allow_all=false → deny all
    """
    if user_id is None:
        return False
    if settings.telegram_allow_all_users:
        return True
    allow = settings.allowlist_ids
    if not allow:
        return False
    return user_id in allow
