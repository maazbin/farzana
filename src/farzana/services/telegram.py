"""Telegram Bot API client — uses only config (PUBLIC_BASE_URL lives in settings)."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import httpx

from farzana.core.config import Settings

DEFAULT_TIMEOUT = httpx.Timeout(90.0, connect=25.0)


class TelegramNetworkError(RuntimeError):
    """Cannot reach api.telegram.org."""


class TelegramClient:
    def __init__(self, settings: Settings):
        self.token = settings.telegram_bot_token
        self.base = f"https://api.telegram.org/bot{self.token}"
        self.file_base = f"https://api.telegram.org/file/bot{self.token}"
        self._timeout = DEFAULT_TIMEOUT

    def _client(self) -> httpx.Client:
        from farzana.core.config import get_settings

        s = get_settings()
        proxy = (s.https_proxy or s.http_proxy or "").strip() or None
        return httpx.Client(timeout=self._timeout, trust_env=True, proxy=proxy)

    def _network_error(self, exc: Exception) -> TelegramNetworkError:
        return TelegramNetworkError(
            "Cannot reach api.telegram.org (timeout or blocked).\n"
            f"  Detail: {type(exc).__name__}: {exc}"
        )

    def _post(self, method: str, payload: dict[str, Any] | None = None, *, retries: int = 3, files=None) -> dict[str, Any]:
        if not self.token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
        last: Exception | None = None
        for attempt in range(1, retries + 1):
            try:
                with self._client() as client:
                    if files:
                        r = client.post(f"{self.base}/{method}", data=payload or {}, files=files)
                    else:
                        r = client.post(f"{self.base}/{method}", json=payload or {})
                    r.raise_for_status()
                    data = r.json()
                    if not data.get("ok"):
                        raise RuntimeError(f"Telegram error: {data}")
                    return data
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last = e
                if attempt < retries:
                    time.sleep(1.5 * attempt)
                    continue
                raise self._network_error(e) from e
        raise self._network_error(last or RuntimeError("unknown"))

    def _get(self, method: str, *, retries: int = 3) -> dict[str, Any]:
        if not self.token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
        last: Exception | None = None
        for attempt in range(1, retries + 1):
            try:
                with self._client() as client:
                    r = client.get(f"{self.base}/{method}")
                    r.raise_for_status()
                    return r.json()
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last = e
                if attempt < retries:
                    time.sleep(1.5 * attempt)
                    continue
                raise self._network_error(e) from e
        raise self._network_error(last or RuntimeError("unknown"))

    def send_message(self, chat_id: int, text: str) -> None:
        self._post("sendMessage", {"chat_id": chat_id, "text": text[:4000]})

    def send_voice(self, chat_id: int, ogg_path: Path) -> None:
        with ogg_path.open("rb") as f:
            self._post(
                "sendVoice",
                {"chat_id": str(chat_id)},
                files={"voice": (ogg_path.name, f, "audio/ogg")},
            )

    def get_file(self, file_id: str) -> dict[str, Any]:
        return self._post("getFile", {"file_id": file_id})

    def download_file(self, file_path: str, dest: Path) -> Path:
        dest.parent.mkdir(parents=True, exist_ok=True)
        url = f"{self.file_base}/{file_path}"
        with self._client() as client:
            r = client.get(url)
            r.raise_for_status()
            dest.write_bytes(r.content)
        return dest

    def set_webhook(self, url: str) -> dict[str, Any]:
        return self._post(
            "setWebhook",
            {
                "url": url,
                "allowed_updates": ["message"],
                "drop_pending_updates": True,
            },
        )

    def get_me(self) -> dict[str, Any]:
        return self._get("getMe")

    def get_webhook_info(self) -> dict[str, Any]:
        return self._get("getWebhookInfo")


def register_webhook_from_settings(settings: Settings) -> str:
    if not settings.webhook_url:
        raise RuntimeError(
            "PUBLIC_BASE_URL is empty in .env. "
            "Set it to your public https base (no path), then restart."
        )
    tg = TelegramClient(settings)
    me = tg.get_me()
    username = (me.get("result") or {}).get("username", "?")
    result = tg.set_webhook(settings.webhook_url)
    if result.get("ok") is False:
        raise RuntimeError(f"setWebhook failed: {result}")
    return f"@{username} → {settings.webhook_url}"
