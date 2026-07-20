"""
FastAPI application factory.

  uv run farzana
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from farzana.api.router import api_router
from farzana.core.config import get_settings
from farzana.core.logging import setup_logging
from farzana.services import vault as vault_io
from farzana.services.scheduler import start_scheduler, stop_scheduler

log = logging.getLogger("farzana")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    settings = get_settings()
    vault_io.ensure_vault(settings.vault_path)
    log.info("vault ready at %s", settings.vault_path.resolve())
    log.info("webhook path: %s", settings.webhook_path)
    log.info("allow_all_users=%s", settings.telegram_allow_all_users)
    if settings.celery_task_always_eager:
        log.info("CELERY_TASK_ALWAYS_EAGER=true — tasks run in-process")
    start_scheduler(settings)
    yield
    stop_scheduler()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Farzana",
        version="0.2.0",
        description="Farzana — listens carefully. Voice, memory, proactive resurfacing.",
        lifespan=lifespan,
    )
    app.include_router(api_router)
    return app


app = create_app()
