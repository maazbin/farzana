"""Telegram webhook — single-user; voice/audio/document audio for listen mode."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from farzana.api.deps import settings_dep
from farzana.core.config import Settings
from farzana.core.security import is_allowed_user
from farzana.services.telegram import TelegramClient
from farzana.workers.tasks import handle_text_message, handle_voice_message

log = logging.getLogger(__name__)
router = APIRouter(tags=["telegram"])


def _audio_file_id(message: dict) -> tuple[str, str] | None:
    """Return (file_id, kind) for voice, audio, or audio document."""
    if message.get("voice"):
        return message["voice"]["file_id"], "voice"
    if message.get("audio"):
        return message["audio"]["file_id"], "audio"
    doc = message.get("document") or {}
    mime = (doc.get("mime_type") or "").lower()
    if doc.get("file_id") and mime.startswith("audio/"):
        return doc["file_id"], "document"
    # some clients send video_note — skip for now
    return None


@router.post("/telegram/{secret}")
async def telegram_webhook(
    secret: str,
    request: Request,
    settings: Settings = Depends(settings_dep),
) -> dict:
    if secret != settings.telegram_webhook_secret:
        raise HTTPException(status_code=404, detail="not found")

    update = await request.json()
    message = update.get("message") or update.get("edited_message")
    if not message:
        return {"ok": True, "ignored": True}

    user = message.get("from") or {}
    user_id = user.get("id")
    username = user.get("username") or user.get("first_name") or ""
    chat = message.get("chat") or {}
    chat_id = chat.get("id")

    if not is_allowed_user(user_id, settings):
        log.warning("rejected user_id=%s (owner=%s)", user_id, settings.owner_user_id)
        if chat_id and settings.telegram_bot_token:
            try:
                TelegramClient(settings).send_message(
                    chat_id,
                    "This Farzana is private — single-user only.",
                )
            except Exception:
                log.exception("notify unauthorized failed")
        return {"ok": True, "authorized": False}

    audio = _audio_file_id(message)
    if audio and chat_id:
        file_id, kind = audio
        handle_voice_message.delay(chat_id, user_id, file_id, username, kind)
        return {"ok": True, "type": kind, "queued": True}

    text = message.get("text")
    if text and chat_id:
        handle_text_message.delay(chat_id, user_id, text, username, False)
        return {"ok": True, "queued": True}

    if chat_id:
        handle_text_message.delay(
            chat_id,
            user_id,
            "(unsupported type — send text, voice, or audio file; /listen for long capture)",
            username,
            False,
        )
    return {"ok": True, "type": "other"}
