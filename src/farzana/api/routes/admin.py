"""Admin helpers for local / ops (webhook registration)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from farzana.api.deps import settings_dep
from farzana.core.config import Settings
from farzana.services.telegram import TelegramClient

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/set-webhook")
def set_webhook(settings: Settings = Depends(settings_dep)) -> dict:
    """Call after ngrok is up and PUBLIC_BASE_URL is set in .env."""
    if not settings.webhook_url:
        raise HTTPException(
            status_code=400,
            detail="Set PUBLIC_BASE_URL in .env to your ngrok https URL (no path)",
        )
    tg = TelegramClient(settings)
    result = tg.set_webhook(settings.webhook_url)
    return {"webhook_url": settings.webhook_url, "telegram": result}


@router.get("/webhook-info")
def webhook_info(settings: Settings = Depends(settings_dep)) -> dict:
    tg = TelegramClient(settings)
    return tg.get_webhook_info()
