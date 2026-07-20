"""Application settings loaded from environment / `.env`."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "local"
    public_base_url: str = ""
    vault_path: Path = Path("./vault")
    log_level: str = "INFO"
    user_display_name: str = "there"

    telegram_bot_token: str = ""
    # Empty + allow_all_users=true → anyone can use the bot
    telegram_allowlist_user_ids: str = ""
    telegram_allow_all_users: bool = True
    telegram_webhook_secret: str = "change-me"

    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4.1-mini"
    openai_tts_model: str = "gpt-4o-mini-tts"
    openai_tts_voice: str = "alloy"
    openai_stt_model: str = "whisper-1"
    openai_embedding_model: str = "text-embedding-3-small"

    # Prefer voice replies when user sent voice, or always if true
    voice_replies: bool = True
    voice_replies_always: bool = False

    redis_url: str = "redis://127.0.0.1:6379/0"
    celery_task_always_eager: bool = True

    # Proactive (in-process scheduler)
    proactive_enabled: bool = True
    proactive_max_per_day: int = 3
    morning_brief_hour_utc: int = 7
    evening_debrief_hour_utc: int = 19
    proactive_scan_minutes: int = 60

    https_proxy: str = ""
    http_proxy: str = ""

    @field_validator("vault_path", mode="before")
    @classmethod
    def _vault_path(cls, v: str | Path) -> Path:
        return Path(v)

    @property
    def allowlist_ids(self) -> set[int]:
        raw = self.telegram_allowlist_user_ids.strip()
        if not raw:
            return set()
        return {int(x.strip()) for x in raw.split(",") if x.strip()}

    @property
    def webhook_path(self) -> str:
        return f"/telegram/{self.telegram_webhook_secret}"

    @property
    def webhook_url(self) -> str | None:
        base = self.public_base_url.rstrip("/")
        if not base:
            return None
        return f"{base}{self.webhook_path}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
