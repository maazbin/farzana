"""FastAPI dependencies."""

from __future__ import annotations

from farzana.core.config import Settings, get_settings


def settings_dep() -> Settings:
    return get_settings()
