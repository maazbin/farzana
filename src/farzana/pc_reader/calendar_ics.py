"""Parse .ics exports → Markdown (read-only). No calendar write APIs."""

from __future__ import annotations

import re
from pathlib import Path


def _unfold(text: str) -> str:
    # RFC 5545 line folding: CRLF + space/tab
    return re.sub(r"\r?\n[ \t]", "", text)


def _unescape(value: str) -> str:
    return (
        value.replace("\\n", "\n")
        .replace("\\,", ",")
        .replace("\\;", ";")
        .replace("\\\\", "\\")
    )


def _props(block: str) -> dict[str, str]:
    """Parse simple KEY:VALUE / KEY;params:VALUE lines inside a VEVENT."""
    out: dict[str, str] = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        left, right = line.split(":", 1)
        key = left.split(";", 1)[0].upper()
        # last wins for simple fields
        out[key] = _unescape(right.strip())
    return out


def parse_ics(path: Path) -> list[dict]:
    raw = _unfold(path.read_text(encoding="utf-8", errors="ignore"))
    events: list[dict] = []
    for m in re.finditer(r"BEGIN:VEVENT(.*?)END:VEVENT", raw, re.DOTALL | re.IGNORECASE):
        p = _props(m.group(1))
        summary = p.get("SUMMARY") or "(no title)"
        events.append(
            {
                "summary": summary,
                "dtstart": p.get("DTSTART", ""),
                "dtend": p.get("DTEND", ""),
                "location": p.get("LOCATION", ""),
                "description": p.get("DESCRIPTION", ""),
                "uid": p.get("UID", ""),
                "status": p.get("STATUS", ""),
            }
        )
    return events


def events_to_markdown(events: list[dict], *, source_name: str) -> tuple[str, str]:
    """Return (title, body) for vault write."""
    title = f"Calendar - {source_name}"
    if not events:
        return title, "_No VEVENT blocks found in this ICS export._"

    lines = [
        f"_Read-only import from `{source_name}` — Farzana does not book or change events._",
        "",
    ]
    for i, ev in enumerate(events, 1):
        lines.append(f"## {i}. {ev['summary']}")
        lines.append("")
        if ev.get("dtstart"):
            when = ev["dtstart"]
            if ev.get("dtend"):
                when = f"{when} -> {ev['dtend']}"
            lines.append(f"- **When:** {when}")
        if ev.get("location"):
            lines.append(f"- **Where:** {ev['location']}")
        if ev.get("status"):
            lines.append(f"- **Status:** {ev['status']}")
        if ev.get("uid"):
            lines.append(f"- **UID:** `{ev['uid']}`")
        if ev.get("description"):
            lines.append("")
            lines.append(ev["description"].strip())
        lines.append("")
    return title, "\n".join(lines).strip()


def ics_file_to_markdown(path: Path) -> tuple[str, str]:
    events = parse_ics(path)
    return events_to_markdown(events, source_name=path.name)
