"""Watch a drop folder for ICS / EML / MD / TXT — read-only ingest into vault."""

from __future__ import annotations

import logging
import time
from pathlib import Path

from farzana.pc_reader import calendar_ics, mail_eml
from farzana.pc_reader.ingest import (
    already_ingested,
    ensure_pc_dirs,
    mark_ingested,
    write_pc_markdown,
)

log = logging.getLogger(__name__)

SUPPORTED = {".ics", ".eml", ".md", ".txt", ".markdown"}


def process_file(path: Path, vault: Path) -> Path | None:
    """Ingest one file. Returns output path or None if skipped."""
    if not path.is_file():
        return None
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED:
        log.debug("skip unsupported %s", path.name)
        return None
    if already_ingested(vault, path):
        log.debug("already ingested %s", path.name)
        return None

    ensure_pc_dirs(vault)
    source = str(path.resolve())

    try:
        if suffix == ".ics":
            title, body = calendar_ics.ics_file_to_markdown(path)
            out = write_pc_markdown(
                vault,
                "calendar",
                title,
                body,
                source_file=source,
                extra_front={"format": "ics"},
            )
        elif suffix == ".eml":
            title, body = mail_eml.eml_to_markdown(path)
            out = write_pc_markdown(
                vault,
                "mail",
                title,
                body,
                source_file=source,
                extra_front={"format": "eml"},
            )
        else:
            # markdown / text drops you choose
            text = path.read_text(encoding="utf-8", errors="ignore")
            title = f"File - {path.stem}"
            body = (
                f"_Read-only drop from `{path.name}`._\n\n"
                + (text.strip() or "_(empty)_")
            )
            if len(body) > 20000:
                body = body[:20000] + "\n\n… _(truncated)_"
            out = write_pc_markdown(
                vault,
                "files",
                title,
                body,
                source_file=source,
                extra_front={"format": suffix.lstrip(".")},
            )
    except Exception:
        log.exception("failed to ingest %s", path)
        return None

    mark_ingested(vault, path, out)
    log.info("ingested %s → %s", path.name, out)
    return out


def scan_folder(watch_dir: Path, vault: Path) -> list[Path]:
    """Process all supported files once (non-recursive top level + one level deep)."""
    watch_dir = watch_dir.expanduser().resolve()
    vault = vault.expanduser().resolve()
    if not watch_dir.is_dir():
        raise FileNotFoundError(f"watch folder not found: {watch_dir}")

    ensure_pc_dirs(vault)
    results: list[Path] = []
    candidates: list[Path] = []
    for p in sorted(watch_dir.iterdir()):
        if p.is_file():
            candidates.append(p)
        elif p.is_dir() and not p.name.startswith("."):
            for child in sorted(p.iterdir()):
                if child.is_file():
                    candidates.append(child)

    for path in candidates:
        out = process_file(path, vault)
        if out:
            results.append(out)
    return results


def watch_loop(
    watch_dir: Path,
    vault: Path,
    *,
    interval_sec: float = 15.0,
    once: bool = False,
) -> None:
    """
    Poll the drop folder. No write to external systems.
    Uses polling so we stay stdlib-only (no watchdog dependency).
    """
    watch_dir = watch_dir.expanduser().resolve()
    vault = vault.expanduser().resolve()
    log.info("PC reader watching %s → vault %s (interval=%.0fs)", watch_dir, vault, interval_sec)

    while True:
        try:
            done = scan_folder(watch_dir, vault)
            if done:
                log.info("ingested %d file(s)", len(done))
        except Exception:
            log.exception("scan failed")
        if once:
            break
        time.sleep(max(2.0, interval_sec))
