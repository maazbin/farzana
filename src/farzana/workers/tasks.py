"""Celery / eager tasks — messages, voice, close, proactive."""

from __future__ import annotations

import logging
import re
import tempfile
from pathlib import Path

from farzana.core.config import get_settings
from farzana.services import capture, dialogue, extract, stt, tts, vault as vault_io
from farzana.services.proactive import run_brief, run_promise_scan
from farzana.services.telegram import TelegramClient
from farzana.workers.celery_app import celery_app

log = logging.getLogger(__name__)

NOTE_RE = re.compile(
    r"^(?:/note(?:@\w+)?\s+|note this:\s*)(.+)$",
    re.IGNORECASE | re.DOTALL,
)
CLOSE_RE = re.compile(
    r"^(?:/close(?:@\w+)?(?:\s+(.+))?|close notes(?:\s*:\s*(.+))?)$",
    re.IGNORECASE,
)


def _send_reply(settings, tg: TelegramClient, chat_id: int, text: str, *, prefer_voice: bool) -> None:
    use_voice = prefer_voice and (settings.voice_replies or settings.voice_replies_always)
    if settings.voice_replies_always:
        use_voice = settings.voice_replies
    if use_voice and settings.openai_api_key:
        try:
            tmp = Path(tempfile.gettempdir()) / f"farzana-out-{chat_id}.ogg"
            tts.synthesize_to_file(settings, text, tmp)
            tg.send_voice(chat_id, tmp)
            return
        except Exception:
            log.exception("voice reply failed; text fallback")
    tg.send_message(chat_id, text)


@celery_app.task(name="farzana.handle_text_message")
def handle_text_message(
    chat_id: int,
    user_id: int,
    text: str,
    username: str = "",
    prefer_voice: bool = False,
) -> dict:
    settings = get_settings()
    tg = TelegramClient(settings)
    vault_io.register_user(settings.vault_path, user_id, chat_id, username)
    raw = (text or "").strip()
    if not raw:
        return {"ok": False, "reason": "empty"}

    name = username or settings.user_display_name

    if raw.lower().startswith("/start"):
        reply = (
            f"Farzana here. Hello {name}.\n\n"
            "I listen carefully — text or voice notes.\n\n"
            "• Send text or a voice message\n"
            "• Note this: meeting name — open a session\n"
            "• /close — close session & extract promises\n"
            "• /brief — morning-style brief now\n"
            "• /quiet — pause proactive messages\n"
            "• /help — commands\n\n"
            "I remember and can resurface open loops. I don't act outside your vault."
        )
        _send_reply(settings, tg, chat_id, reply, prefer_voice=prefer_voice)
        return {"ok": True, "cmd": "start"}

    if raw.lower().startswith("/help"):
        reply = (
            "Farzana commands:\n"
            "/start — hello\n"
            "/help — this\n"
            "/note <name> — open session\n"
            "Note this: <name> — same\n"
            "/close [name] — close session + extract\n"
            "/brief — discuss open loops now\n"
            "/quiet — stop proactive for you\n"
            "/voice on|off — prefer voice replies\n"
            "Voice notes — transcribed & stored\n"
            "Plain text — stored + discussion reply"
        )
        _send_reply(settings, tg, chat_id, reply, prefer_voice=prefer_voice)
        return {"ok": True, "cmd": "help"}

    if raw.lower().startswith("/quiet"):
        vault_io.log_pattern_event(settings.vault_path, user_id, "quiet_requested")
        # mark quiet in profile
        ur = vault_io.user_root(settings.vault_path, user_id)
        prof = ur / "profile.md"
        textp = prof.read_text(encoding="utf-8") if prof.exists() else "---\nquiet: true\n---\n"
        lines = []
        found = False
        for line in textp.splitlines():
            if line.startswith("quiet:"):
                lines.append("quiet: true")
                found = True
            else:
                lines.append(line)
        if not found:
            lines.insert(1, "quiet: true")
        prof.write_text("\n".join(lines) + "\n", encoding="utf-8")
        _send_reply(settings, tg, chat_id, "Quiet mode on. I won't initiate until you message again.", prefer_voice=prefer_voice)
        return {"ok": True, "cmd": "quiet"}

    if raw.lower().startswith("/voice"):
        on = "off" not in raw.lower()
        settings_note = "on" if on else "off"
        # store in profile
        ur = vault_io.user_root(settings.vault_path, user_id)
        prof = ur / "profile.md"
        textp = prof.read_text(encoding="utf-8") if prof.exists() else "---\nvoice: true\n---\n"
        lines = []
        found = False
        for line in textp.splitlines():
            if line.startswith("voice:"):
                lines.append(f"voice: {'true' if on else 'false'}")
                found = True
            else:
                lines.append(line)
        if not found:
            lines.insert(1, f"voice: {'true' if on else 'false'}")
        prof.write_text("\n".join(lines) + "\n", encoding="utf-8")
        _send_reply(settings, tg, chat_id, f"Voice replies {settings_note}.", prefer_voice=False)
        return {"ok": True, "cmd": "voice"}

    if raw.lower().startswith("/brief"):
        text_out = dialogue.brief_text(settings, user_id, kind="morning")
        _send_reply(settings, tg, chat_id, text_out, prefer_voice=prefer_voice or settings.voice_replies)
        vault_io.log_proactive(settings.vault_path, user_id, "manual_brief", text_out)
        return {"ok": True, "cmd": "brief"}

    cm = CLOSE_RE.match(raw)
    if cm:
        name_part = (cm.group(1) or cm.group(2) or "").strip()
        if not name_part:
            opens = vault_io.list_open_sessions(settings.vault_path, user_id)
            if not opens:
                _send_reply(settings, tg, chat_id, "No open session. Use: /close session-name", prefer_voice=prefer_voice)
                return {"ok": False, "reason": "no session"}
            path = opens[-1]
            name_part = path.stem
        else:
            path = vault_io.close_session(settings.vault_path, user_id, name_part)
            if not path:
                # try close by slug
                path = vault_io.user_root(settings.vault_path, user_id) / "sessions" / f"{name_part}.md"
        if path and path.exists():
            vault_io.close_session(settings.vault_path, user_id, name_part)
            session_text = path.read_text(encoding="utf-8", errors="ignore")
            summary = extract.extract_and_store(settings, user_id, session_text, name_part)
            _send_reply(settings, tg, chat_id, summary, prefer_voice=prefer_voice)
            vault_io.log_pattern_event(settings.vault_path, user_id, f"close:{name_part}")
            return {"ok": True, "cmd": "close", "session": name_part}
        _send_reply(settings, tg, chat_id, f"Session not found: {name_part}", prefer_voice=prefer_voice)
        return {"ok": False}

    session_name: str | None = None
    body = raw
    m = NOTE_RE.match(raw)
    if m:
        session_name = m.group(1).strip()
        if "\n" in session_name:
            title, rest = session_name.split("\n", 1)
            session_name = title.strip()
            body = rest.strip() or f"(opened session: {session_name})"
        else:
            body = f"(session open/continue: {session_name})"

    try:
        note = capture.capture_text(
            settings.vault_path,
            user_id,
            body,
            session_name=session_name,
        )
        vault_io.log_pattern_event(settings.vault_path, user_id, f"capture:{note}")
        if session_name and body.startswith("(session open"):
            reply = f"Session '{session_name}' ready. Send notes or voice; /close when done."
        else:
            reply = dialogue.reply_text(
                settings,
                raw if not session_name else f"[session {session_name}] {body}",
                user_id=user_id,
                context_note=f"captured to {note}",
                display_name=name,
            )
        _send_reply(settings, tg, chat_id, reply, prefer_voice=prefer_voice)
        return {"ok": True, "note": note}
    except Exception:
        log.exception("handle_text_message failed")
        try:
            tg.send_message(chat_id, "Something failed on my side. Try again shortly.")
        except Exception:
            log.exception("failed to notify user")
        return {"ok": False}


@celery_app.task(name="farzana.handle_voice_message")
def handle_voice_message(
    chat_id: int,
    user_id: int,
    file_id: str,
    username: str = "",
) -> dict:
    settings = get_settings()
    tg = TelegramClient(settings)
    vault_io.register_user(settings.vault_path, user_id, chat_id, username)
    try:
        meta = tg.get_file(file_id)
        file_path = (meta.get("result") or {}).get("file_path")
        if not file_path:
            tg.send_message(chat_id, "Could not download that voice note.")
            return {"ok": False}
        dest = Path(tempfile_dir()) / f"voice-{user_id}-{file_id[:12]}.ogg"
        tg.download_file(file_path, dest)
        text = stt.transcribe_file(settings, dest)
        if not text:
            tg.send_message(chat_id, "I heard the note but couldn't transcribe it.")
            return {"ok": False}
        # Process as text with voice preference for reply
        return handle_text_message(
            chat_id,
            user_id,
            text,
            username=username,
            prefer_voice=True,
        )
    except Exception:
        log.exception("handle_voice_message failed")
        try:
            tg.send_message(chat_id, "Voice processing failed. Send text if you can.")
        except Exception:
            pass
        return {"ok": False}


def tempfile_dir() -> str:
    import tempfile

    d = Path(tempfile.gettempdir()) / "farzana"
    d.mkdir(exist_ok=True)
    return str(d)


@celery_app.task(name="farzana.proactive_morning")
def proactive_morning() -> dict:
    n = run_brief(get_settings(), "morning")
    return {"sent": n}


@celery_app.task(name="farzana.proactive_evening")
def proactive_evening() -> dict:
    n = run_brief(get_settings(), "evening")
    return {"sent": n}


@celery_app.task(name="farzana.proactive_scan")
def proactive_scan() -> dict:
    n = run_promise_scan(get_settings())
    return {"sent": n}
