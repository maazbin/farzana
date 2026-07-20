"""Tasks — single-user: listen mode, voice, close, proactive."""

from __future__ import annotations

import logging
import re
import tempfile
from pathlib import Path

from farzana.core.config import get_settings
from farzana.services import capture, dialogue, extract, listen, stt, tts, vault as vault_io
from farzana.services.proactive import run_brief, run_promise_scan
from farzana.services.telegram import TelegramClient
from farzana.workers.celery_app import celery_app

log = logging.getLogger(__name__)

NOTE_RE = re.compile(
    r"^(?:/note(?:@\w+)?\s+|note this:\s*)(.+)$",
    re.IGNORECASE | re.DOTALL,
)
LISTEN_RE = re.compile(
    r"^(?:/listen(?:@\w+)?(?:\s+(.+))?|listen(?:\s*:\s*(.+))?)$",
    re.IGNORECASE,
)
CLOSE_RE = re.compile(
    r"^(?:/close(?:@\w+)?(?:\s+(.+))?|close notes(?:\s*:\s*(.+))?)$",
    re.IGNORECASE,
)
STOP_RE = re.compile(r"^/(?:stop|stoplisten)(?:@\w+)?\s*$", re.IGNORECASE)


def _send_reply(settings, tg: TelegramClient, chat_id: int, text: str, *, prefer_voice: bool) -> None:
    use_voice = prefer_voice and settings.voice_replies
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
    vault_io.set_chat_id(settings.vault_path, chat_id)
    raw = (text or "").strip()
    if not raw:
        return {"ok": False, "reason": "empty"}

    name = username or settings.user_display_name

    if raw.lower().startswith("/start"):
        reply = (
            f"Farzana here. Hello {name}.\n\n"
            "I listen carefully — like a Pocket session on Telegram.\n\n"
            "• /listen Meeting name — then send long voice/audio clips\n"
            "• Keep sending voice while listening (chunks append)\n"
            "• /stop — end listen · /close — extract promises\n"
            "• /brief · /quiet · text anytime\n\n"
            "I remember, remind, adapt, discuss. I don't act on email/calendar."
        )
        _send_reply(settings, tg, chat_id, reply, prefer_voice=prefer_voice)
        return {"ok": True, "cmd": "start"}

    if raw.lower().startswith("/help"):
        reply = (
            "Farzana (personal listen + memory):\n"
            "/listen [name] — Pocket-style session (long audio)\n"
            "/stop — leave listen mode\n"
            "/note <name> · Note this: <name>\n"
            "/close [name] — close + extract\n"
            "/brief · /quiet · /voice on|off\n"
            "Long voice/audio files append while listening"
        )
        _send_reply(settings, tg, chat_id, reply, prefer_voice=prefer_voice)
        return {"ok": True, "cmd": "help"}

    lm = LISTEN_RE.match(raw)
    if lm:
        title = (lm.group(1) or lm.group(2) or "listen").strip() or "listen"
        session = listen.start_listen(settings.vault_path, title)
        reply = (
            f"Listening: '{session}'.\n\n"
            "Hold Telegram record as long as you need (or send an audio file). "
            "Send more clips anytime — they append to this session.\n"
            "When done: /stop or /close"
        )
        tg.send_message(chat_id, reply)
        vault_io.log_pattern_event(settings.vault_path, f"listen_start:{session}")
        return {"ok": True, "cmd": "listen", "session": session}

    if STOP_RE.match(raw):
        session = listen.stop_listen(settings.vault_path)
        if not session:
            tg.send_message(chat_id, "I wasn't in listen mode.")
            return {"ok": False}
        tg.send_message(
            chat_id,
            f"Stopped listening on '{session}'. Send /close {session} to extract promises, or keep chatting.",
        )
        vault_io.log_pattern_event(settings.vault_path, f"listen_stop:{session}")
        return {"ok": True, "cmd": "stop", "session": session}

    if raw.lower().startswith("/quiet"):
        vault_io.set_flag(settings.vault_path, "quiet", "true")
        vault_io.log_pattern_event(settings.vault_path, "quiet_requested")
        _send_reply(
            settings,
            tg,
            chat_id,
            "Quiet mode on. I won't initiate until you message again.",
            prefer_voice=prefer_voice,
        )
        return {"ok": True, "cmd": "quiet"}

    if raw.lower().startswith("/voice"):
        on = "off" not in raw.lower()
        vault_io.set_flag(settings.vault_path, "voice", "true" if on else "false")
        _send_reply(settings, tg, chat_id, f"Voice replies {'on' if on else 'off'}.", prefer_voice=False)
        return {"ok": True, "cmd": "voice"}

    if raw.lower().startswith("/brief"):
        text_out = dialogue.brief_text(settings, kind="morning")
        _send_reply(settings, tg, chat_id, text_out, prefer_voice=prefer_voice or settings.voice_replies)
        vault_io.log_proactive(settings.vault_path, "manual_brief", text_out)
        return {"ok": True, "cmd": "brief"}

    cm = CLOSE_RE.match(raw)
    if cm:
        # closing also ends listen mode
        listen_session = listen.stop_listen(settings.vault_path)
        name_part = (cm.group(1) or cm.group(2) or "").strip() or (listen_session or "")
        if not name_part:
            opens = vault_io.list_open_sessions(settings.vault_path)
            if not opens:
                _send_reply(
                    settings,
                    tg,
                    chat_id,
                    "No open session. Use: /close session-name",
                    prefer_voice=prefer_voice,
                )
                return {"ok": False, "reason": "no session"}
            name_part = opens[-1].stem
        path = vault_io.close_session(settings.vault_path, name_part)
        if path and path.exists():
            session_text = path.read_text(encoding="utf-8", errors="ignore")
            summary = extract.extract_and_store(settings, session_text, name_part)
            _send_reply(settings, tg, chat_id, summary, prefer_voice=prefer_voice)
            vault_io.log_pattern_event(settings.vault_path, f"close:{name_part}")
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
        note = capture.capture_text(settings.vault_path, body, session_name=session_name)
        vault_io.log_pattern_event(settings.vault_path, f"capture:{note}")
        if session_name and body.startswith("(session open"):
            reply = f"Session '{session_name}' ready. Or /listen {session_name} for long audio."
        else:
            reply = dialogue.reply_text(
                settings,
                raw if not session_name else f"[session {session_name}] {body}",
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
    file_kind: str = "voice",
) -> dict:
    """
    Voice/audio ingest.
    If listen mode active → append transcript quietly (Pocket-style).
    Else → normal capture + discussion reply.
    """
    settings = get_settings()
    tg = TelegramClient(settings)
    vault_io.set_chat_id(settings.vault_path, chat_id)
    try:
        meta = tg.get_file(file_id)
        file_path = (meta.get("result") or {}).get("file_path")
        if not file_path:
            tg.send_message(chat_id, "Could not download that audio.")
            return {"ok": False}

        suffix = Path(file_path).suffix or (".ogg" if file_kind == "voice" else ".mp3")
        dest = Path(tempfile.gettempdir()) / "farzana" / f"audio-{file_id[:16]}{suffix}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        tg.download_file(file_path, dest)

        text = stt.transcribe_file(settings, dest)
        if not text:
            tg.send_message(chat_id, "I got the audio but couldn't transcribe it.")
            return {"ok": False}

        # Pocket-style: listening session absorbs long audio without a long chat reply
        if listen.get_listen_state(settings.vault_path):
            session, n = listen.record_chunk(settings.vault_path, text)
            preview = text if len(text) < 120 else text[:117] + "…"
            tg.send_message(
                chat_id,
                f"Heard chunk {n} → '{session}' ({len(text)} chars).\n{preview}",
            )
            vault_io.log_pattern_event(settings.vault_path, f"listen_chunk:{session}:{n}")
            return {"ok": True, "mode": "listen", "session": session, "chunk": n, "chars": len(text)}

        # Not listening: treat as normal message with voice reply preference
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
            tg.send_message(chat_id, "Audio processing failed. Try a shorter clip or text.")
        except Exception:
            pass
        return {"ok": False}


@celery_app.task(name="farzana.proactive_morning")
def proactive_morning() -> dict:
    return {"sent": run_brief(get_settings(), "morning")}


@celery_app.task(name="farzana.proactive_evening")
def proactive_evening() -> dict:
    return {"sent": run_brief(get_settings(), "evening")}


@celery_app.task(name="farzana.proactive_scan")
def proactive_scan() -> dict:
    return {"sent": run_promise_scan(get_settings())}
