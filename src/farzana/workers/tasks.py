"""Tasks — single-user: semantic modes, listen, voice, close, proactive."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from farzana.core.config import get_settings
from farzana.services import capture, dialogue, extract, listen, stt, tts, vault as vault_io
from farzana.services.intent import Intent, detect_intent
from farzana.services.proactive import run_brief, run_promise_scan
from farzana.services.telegram import TelegramClient
from farzana.workers.celery_app import celery_app

log = logging.getLogger(__name__)

HELP_TEXT = (
    "Farzana — talk naturally (voice or text). I pick up the mode.\n\n"
    "🎙️ Listen / Pocket\n"
    "  • “start listening” · “record this meeting” · /listen Design review\n"
    "  • While listening: send long voice — I save quietly\n"
    "  • Ask me a question anytime — I answer (and still save)\n"
    "  • “stop listening” · “close the session” · /stop · /close\n\n"
    "💬 Everyday\n"
    "  • Just talk — I remember and discuss\n"
    "  • “note this: project-x” · “give me a brief” · “be quiet”\n"
    "  • /voice on|off · /help\n\n"
    "I remember, remind, adapt, discuss. I don't send email or book calendar."
)


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


def _maybe_capture_listen(settings, text: str, intent: Intent) -> tuple[str, int] | None:
    """Append to listen session when intent says so or mode is capture."""
    if not listen.get_listen_state(settings.vault_path):
        return None
    if intent.kind == "capture" or intent.also_capture:
        return listen.record_chunk(settings.vault_path, text)
    return None


def _do_listen_start(settings, tg, chat_id: int, title: str | None, prefer_voice: bool) -> dict:
    name = (title or "listen").strip() or "listen"
    session = listen.start_listen(settings.vault_path, name)
    reply = (
        f"🎙️ Listening: **{session}**\n\n"
        "Send long voice/audio anytime — I'll save it.\n"
        "Ask me something and I'll answer (still saves).\n"
        "When done: say “stop listening” or “close the session”."
    )
    _send_reply(settings, tg, chat_id, reply, prefer_voice=prefer_voice)
    vault_io.log_pattern_event(settings.vault_path, f"listen_start:{session}")
    return {"ok": True, "cmd": "listen", "session": session}


def _do_listen_stop(settings, tg, chat_id: int, prefer_voice: bool) -> dict:
    session = listen.stop_listen(settings.vault_path)
    if not session:
        _send_reply(
            settings,
            tg,
            chat_id,
            "I wasn't in listen mode. Say “start listening” when you want Pocket-style capture.",
            prefer_voice=prefer_voice,
        )
        return {"ok": False, "cmd": "stop"}
    _send_reply(
        settings,
        tg,
        chat_id,
        f"⏹️ Stopped listening on **{session}**.\n"
        f"Say “close the session” or /close {session} to extract promises — or just keep chatting.",
        prefer_voice=prefer_voice,
    )
    vault_io.log_pattern_event(settings.vault_path, f"listen_stop:{session}")
    return {"ok": True, "cmd": "stop", "session": session}


def _do_close(settings, tg, chat_id: int, title: str | None, prefer_voice: bool) -> dict:
    listen_session = listen.stop_listen(settings.vault_path)
    name_part = (title or "").strip() or (listen_session or "")
    if not name_part:
        opens = vault_io.list_open_sessions(settings.vault_path)
        if not opens:
            _send_reply(
                settings,
                tg,
                chat_id,
                "No open session to close. Start with “note this: name” or “start listening”.",
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


def _dispatch(
    settings,
    tg: TelegramClient,
    chat_id: int,
    user_id: int,
    raw: str,
    *,
    username: str,
    prefer_voice: bool,
    intent: Intent,
) -> dict:
    name = username or settings.user_display_name
    kind = intent.kind

    if kind == "start":
        reply = (
            f"Farzana here. Hello {name}.\n\n"
            "Talk naturally — voice or text. I'll switch modes from what you mean.\n\n"
            + HELP_TEXT
        )
        _send_reply(settings, tg, chat_id, reply, prefer_voice=prefer_voice)
        return {"ok": True, "cmd": "start"}

    if kind == "help":
        _send_reply(settings, tg, chat_id, HELP_TEXT, prefer_voice=prefer_voice)
        return {"ok": True, "cmd": "help"}

    if kind == "listen_start":
        return _do_listen_start(settings, tg, chat_id, intent.title, prefer_voice)

    if kind == "listen_stop":
        return _do_listen_stop(settings, tg, chat_id, prefer_voice)

    if kind == "close":
        return _do_close(settings, tg, chat_id, intent.title, prefer_voice)

    if kind == "quiet":
        vault_io.set_flag(settings.vault_path, "quiet", "true")
        vault_io.log_pattern_event(settings.vault_path, "quiet_requested")
        _send_reply(
            settings,
            tg,
            chat_id,
            "🤫 Quiet mode on. I won't initiate until you say “message me again” or just chat.",
            prefer_voice=prefer_voice,
        )
        return {"ok": True, "cmd": "quiet"}

    if kind == "unquiet":
        vault_io.set_flag(settings.vault_path, "quiet", "false")
        vault_io.log_pattern_event(settings.vault_path, "unquiet")
        _send_reply(
            settings,
            tg,
            chat_id,
            "Okay — proactive messages can resume (still capped per day).",
            prefer_voice=prefer_voice,
        )
        return {"ok": True, "cmd": "unquiet"}

    if kind == "voice_on":
        vault_io.set_flag(settings.vault_path, "voice", "true")
        _send_reply(settings, tg, chat_id, "Voice replies on.", prefer_voice=False)
        return {"ok": True, "cmd": "voice"}

    if kind == "voice_off":
        vault_io.set_flag(settings.vault_path, "voice", "false")
        _send_reply(settings, tg, chat_id, "Voice replies off.", prefer_voice=False)
        return {"ok": True, "cmd": "voice"}

    if kind == "brief":
        text_out = dialogue.brief_text(settings, kind="morning")
        _send_reply(settings, tg, chat_id, text_out, prefer_voice=prefer_voice or settings.voice_replies)
        vault_io.log_proactive(settings.vault_path, "manual_brief", text_out)
        return {"ok": True, "cmd": "brief"}

    if kind == "note":
        session_name = (intent.title or "note").strip()
        body = intent.body or f"(session open/continue: {session_name})"
        if intent.body and "\n" in intent.body:
            title, rest = intent.body.split("\n", 1)
            session_name = title.strip() or session_name
            body = rest.strip() or f"(opened session: {session_name})"
        note = capture.capture_text(settings.vault_path, body, session_name=session_name)
        vault_io.log_pattern_event(settings.vault_path, f"capture:{note}")
        _send_reply(
            settings,
            tg,
            chat_id,
            f"📝 Session **{session_name}** ready. "
            f"Say “start listening” for long audio, or just keep talking.",
            prefer_voice=prefer_voice,
        )
        return {"ok": True, "cmd": "note", "session": session_name, "note": note}

    if kind == "capture":
        # Pure listen content
        chunk = _maybe_capture_listen(settings, raw, intent)
        if chunk:
            session, n = chunk
            # Short ack — do not dump full transcript (that felt like a broken reply)
            preview = raw if len(raw) < 80 else raw[:77] + "…"
            tg.send_message(chat_id, f"👂 Saved clip {n} → **{session}**\n_{preview}_")
            vault_io.log_pattern_event(settings.vault_path, f"listen_chunk:{session}:{n}")
            return {"ok": True, "mode": "listen", "session": session, "chunk": n, "chars": len(raw)}
        # Fallback if listen somehow off
        intent = Intent(kind="discuss", body=raw, source="fallback")

    # discuss (default) — optional capture if still in listen + also_capture
    chunk_info = _maybe_capture_listen(settings, raw, intent)
    try:
        if chunk_info:
            session, n = chunk_info
            vault_io.log_pattern_event(settings.vault_path, f"listen_chunk:{session}:{n}")
            context_note = f"also saved as listen clip {n} in session {session}"
        else:
            note = capture.capture_text(settings.vault_path, raw, session_name=None)
            vault_io.log_pattern_event(settings.vault_path, f"capture:{note}")
            context_note = f"captured to {note}"

        listen_state = listen.get_listen_state(settings.vault_path)
        if listen_state:
            context_note += (
                f" | listen mode still ON for '{listen_state.get('session')}'. "
                "User may be asking you something while recording."
            )

        reply = dialogue.reply_text(
            settings,
            raw,
            context_note=context_note,
            display_name=name,
        )
        if chunk_info:
            session, n = chunk_info
            reply = f"👂 Saved to **{session}** (clip {n}).\n\n{reply}"

        _send_reply(settings, tg, chat_id, reply, prefer_voice=prefer_voice)
        return {
            "ok": True,
            "mode": "discuss",
            "intent": intent.source,
            "listen_chunk": bool(chunk_info),
        }
    except Exception:
        log.exception("discuss path failed")
        try:
            tg.send_message(chat_id, "Something failed on my side. Try again shortly.")
        except Exception:
            log.exception("failed to notify user")
        return {"ok": False}


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

    listen_active = bool(listen.get_listen_state(settings.vault_path))
    intent = detect_intent(
        raw,
        listen_active=listen_active,
        settings=settings,
        use_llm_fallback=True,
    )
    log.info(
        "intent kind=%s source=%s listen=%s",
        intent.kind,
        intent.source,
        listen_active,
    )
    return _dispatch(
        settings,
        tg,
        chat_id,
        user_id,
        raw,
        username=username,
        prefer_voice=prefer_voice,
        intent=intent,
    )


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
    STT → same semantic intent pipeline as text (listen/stop/close/discuss/capture).
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

        # Same path as text — semantics decide mode
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
