"""Telegram webhook — single-user owner only."""

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

    voice = message.get("voice") or message.get("audio")
    if voice and chat_id:
        file_id = voice.get("file_id")
        if file_id:
            handle_voice_message.delay(chat_id, user_id, file_id, username)
            return {"ok": True, "type": "voice", "queued": True}

    text = message.get("text")
    if text and chat_id:
        handle_text_message.delay(chat_id, user_id, text, username, False)
        return {"ok": True, "queued": True}

    if chat_id:
        handle_text_message.delay(
            chat_id,
            user_id,
            "(unsupported message type — send text or a voice note)",
            username,
            False,
        )
    return {"ok": True, "type": "other"}
