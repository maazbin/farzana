"""Health and readiness probes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from farzana.api.deps import settings_dep
from farzana.core.config import Settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health(settings: Settings = Depends(settings_dep)) -> dict:
    return {
        "ok": True,
        "env": settings.app_env,
        "single_user": True,
        "owner_configured": bool(settings.owner_user_id),
        "vault": str(settings.vault_path.resolve()),
        "openai_configured": bool(settings.openai_api_key),
        "telegram_configured": bool(settings.telegram_bot_token),
        "eager": settings.celery_task_always_eager,
        "public_base_url": settings.public_base_url or None,
        "webhook_url": settings.webhook_url,
    }
