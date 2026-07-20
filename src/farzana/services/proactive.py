"""Proactive outreach: briefs + open-promise resurfacing."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from farzana.core.config import Settings
from farzana.services import dialogue, vault as vault_io
from farzana.services.telegram import TelegramClient
from farzana.services import tts as tts_svc

log = logging.getLogger(__name__)


def _today_proactive_count(root: Path, user_id: int) -> int:
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = vault_io.user_root(root, user_id) / "proactive" / f"{day}.md"
    if not path.exists():
        return 0
    return path.read_text(encoding="utf-8").count("**why:**")


def send_to_user(
    settings: Settings,
    chat_id: int,
    user_id: int,
    text: str,
    reason: str,
    *,
    as_voice: bool = False,
) -> None:
    tg = TelegramClient(settings)
    if as_voice and settings.voice_replies:
        try:
            tmp = Path(settings.vault_path) / "tmp" / f"tts-{user_id}.ogg"
            tts_svc.synthesize_to_file(settings, text, tmp)
            tg.send_voice(chat_id, tmp)
        except Exception:
            log.exception("TTS failed; sending text")
            tg.send_message(chat_id, text)
    else:
        tg.send_message(chat_id, text)
    vault_io.log_proactive(settings.vault_path, user_id, reason, text)
    vault_io.log_pattern_event(settings.vault_path, user_id, f"proactive:{reason}")


def _is_quiet(root: Path, user_id: int) -> bool:
    prof = vault_io.user_root(root, user_id) / "profile.md"
    if not prof.exists():
        return False
    return "quiet: true" in prof.read_text(encoding="utf-8", errors="ignore")


def run_brief(settings: Settings, kind: str) -> int:
    if not settings.proactive_enabled:
        return 0
    n = 0
    for u in vault_io.list_registered_users(settings.vault_path):
        uid = u["user_id"]
        chat_id = u.get("chat_id")
        if not chat_id:
            continue
        if _is_quiet(settings.vault_path, uid):
            continue
        if _today_proactive_count(settings.vault_path, uid) >= settings.proactive_max_per_day:
            continue
        try:
            text = dialogue.brief_text(settings, uid, kind=kind)
            send_to_user(
                settings,
                int(chat_id),
                uid,
                text,
                reason=f"{kind}_brief",
                as_voice=settings.voice_replies,
            )
            n += 1
        except Exception:
            log.exception("brief failed user=%s", uid)
    return n


def run_promise_scan(settings: Settings) -> int:
    if not settings.proactive_enabled:
        return 0
    n = 0
    for u in vault_io.list_registered_users(settings.vault_path):
        uid = u["user_id"]
        chat_id = u.get("chat_id")
        if not chat_id:
            continue
        if _is_quiet(settings.vault_path, uid):
            continue
        if _today_proactive_count(settings.vault_path, uid) >= settings.proactive_max_per_day:
            continue
        promises = vault_io.list_open_promises(settings.vault_path, uid)
        if not promises:
            continue
        # Resurface oldest open promise
        p = promises[0]
        title = p.stem
        body = p.read_text(encoding="utf-8", errors="ignore")[:400]
        text = (
            f"Open loop still on file: {title}\n\n"
            f"{body[:280]}\n\n"
            "Want to update status, close it, or discuss next step?"
        )
        try:
            send_to_user(
                settings,
                int(chat_id),
                uid,
                text,
                reason=f"promise:{title}",
                as_voice=settings.voice_replies,
            )
            n += 1
        except Exception:
            log.exception("promise scan failed user=%s", uid)
    return n
