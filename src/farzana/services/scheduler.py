"""In-process proactive scheduler (no Redis required)."""

from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from farzana.core.config import Settings

log = logging.getLogger(__name__)
_scheduler: BackgroundScheduler | None = None


def start_scheduler(settings: Settings) -> BackgroundScheduler | None:
    global _scheduler
    if not settings.proactive_enabled:
        log.info("proactive disabled")
        return None
    if _scheduler and _scheduler.running:
        return _scheduler

    from farzana.workers import tasks as tasks_mod

    sched = BackgroundScheduler(timezone="UTC")
    sched.add_job(
        lambda: tasks_mod.proactive_morning(),
        CronTrigger(hour=settings.morning_brief_hour_utc, minute=0),
        id="morning_brief",
        replace_existing=True,
    )
    sched.add_job(
        lambda: tasks_mod.proactive_evening(),
        CronTrigger(hour=settings.evening_debrief_hour_utc, minute=0),
        id="evening_debrief",
        replace_existing=True,
    )
    sched.add_job(
        lambda: tasks_mod.proactive_scan(),
        IntervalTrigger(minutes=max(15, settings.proactive_scan_minutes)),
        id="promise_scan",
        replace_existing=True,
    )
    sched.start()
    _scheduler = sched
    log.info(
        "proactive scheduler started (morning=%s:00 UTC evening=%s:00 UTC scan=%sm)",
        settings.morning_brief_hour_utc,
        settings.evening_debrief_hour_utc,
        settings.proactive_scan_minutes,
    )
    return sched


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
