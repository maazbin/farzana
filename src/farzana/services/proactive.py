"""Proactive outreach for the single owner."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from farzana.core.config import Settings
from farzana.services import dialogue, vault as vault_io
from farzana.services import tts as tts_svc
from farzana.services.telegram import TelegramClient

log = logging.getLogger(__name__)


def _today_proactive_count(root: Path) -> int:
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = root / "proactive" / f"{day}.md"
    if not path.exists():
        return 0
    return path.read_text(encoding="utf-8").count("**why:**")


def send_owner(
    settings: Settings,
    text: str,
    reason: str,
    *,
    as_voice: bool = False,
) -> bool:
    chat_id = vault_io.get_chat_id(settings.vault_path)
    if not chat_id:
        log.warning("no chat_id saved yet — owner must /start first")
        return False
    tg = TelegramClient(settings)
    if as_voice and settings.voice_replies:
        try:
            tmp = Path(settings.vault_path) / "tmp" / "tts-out.ogg"
            tts_svc.synthesize_to_file(settings, text, tmp)
            tg.send_voice(chat_id, tmp)
        except Exception:
            log.exception("TTS failed; text fallback")
            tg.send_message(chat_id, text)
    else:
        tg.send_message(chat_id, text)
    vault_io.log_proactive(settings.vault_path, reason, text)
    vault_io.log_pattern_event(settings.vault_path, f"proactive:{reason}")
    return True


def run_brief(settings: Settings, kind: str) -> int:
    if not settings.proactive_enabled:
        return 0
    if vault_io.is_quiet(settings.vault_path):
        return 0
    if _today_proactive_count(settings.vault_path) >= settings.proactive_max_per_day:
        return 0
    try:
        text = dialogue.brief_text(settings, kind=kind)
        ok = send_owner(
            settings,
            text,
            reason=f"{kind}_brief",
            as_voice=settings.voice_replies,
        )
        return 1 if ok else 0
    except Exception:
        log.exception("brief failed")
        return 0


def run_promise_scan(settings: Settings) -> int:
    if not settings.proactive_enabled:
        return 0
    if vault_io.is_quiet(settings.vault_path):
        return 0
    if _today_proactive_count(settings.vault_path) >= settings.proactive_max_per_day:
        return 0
    promises = vault_io.list_open_promises(settings.vault_path)
    if not promises:
        return 0
    p = promises[0]
    title = p.stem
    body = p.read_text(encoding="utf-8", errors="ignore")[:400]
    text = (
        f"Open loop still on file: {title}\n\n"
        f"{body[:280]}\n\n"
        "Want to update status, close it, or discuss next step?"
    )
    try:
        ok = send_owner(
            settings,
            text,
            reason=f"promise:{title}",
            as_voice=settings.voice_replies,
        )
        return 1 if ok else 0
    except Exception:
        log.exception("promise scan failed")
        return 0
