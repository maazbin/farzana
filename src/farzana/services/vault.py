"""Markdown vault I/O — single-user source of truth (one vault root)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def ensure_vault(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for rel in (
        "config",
        "inbox",
        "sessions",
        "people",
        "promises/open",
        "promises/closed",
        "ideas",
        "daily",
        "patterns",
        "proactive",
        "graphs",
        "tmp",
    ):
        (root / rel).mkdir(parents=True, exist_ok=True)

    prefs = root / "config" / "preferences.md"
    if not prefs.exists():
        prefs.write_text(
            "# Preferences\n\n"
            "proactivity_level: medium\n"
            "quiet_mode: false\n"
            "voice_reminders: true\n",
            encoding="utf-8",
        )

    profile = root / "config" / "profile.md"
    if not profile.exists():
        profile.write_text(
            "---\n"
            "chat_id: \n"
            "quiet: false\n"
            "voice: true\n"
            f"created: {datetime.now(timezone.utc).isoformat()}\n"
            "---\n",
            encoding="utf-8",
        )


def set_chat_id(root: Path, chat_id: int) -> None:
    ensure_vault(root)
    path = root / "config" / "profile.md"
    text = path.read_text(encoding="utf-8") if path.exists() else "---\nchat_id: \n---\n"
    lines = []
    found = False
    for line in text.splitlines():
        if line.startswith("chat_id:"):
            lines.append(f"chat_id: {chat_id}")
            found = True
        else:
            lines.append(line)
    if not found:
        lines.insert(1, f"chat_id: {chat_id}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    # also registry for simple read
    reg = root / "config" / "chat.json"
    reg.write_text(
        json.dumps({"chat_id": chat_id, "updated": datetime.now(timezone.utc).isoformat()}, indent=2),
        encoding="utf-8",
    )


def get_chat_id(root: Path) -> int | None:
    reg = root / "config" / "chat.json"
    if reg.exists():
        try:
            return int(json.loads(reg.read_text(encoding="utf-8")).get("chat_id"))
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
    prof = root / "config" / "profile.md"
    if prof.exists():
        for line in prof.read_text(encoding="utf-8").splitlines():
            if line.startswith("chat_id:"):
                raw = line.split(":", 1)[1].strip()
                if raw:
                    try:
                        return int(raw)
                    except ValueError:
                        return None
    return None


def is_quiet(root: Path) -> bool:
    prof = root / "config" / "profile.md"
    if not prof.exists():
        return False
    return "quiet: true" in prof.read_text(encoding="utf-8", errors="ignore")


def set_flag(root: Path, key: str, value: str) -> None:
    ensure_vault(root)
    path = root / "config" / "profile.md"
    text = path.read_text(encoding="utf-8") if path.exists() else "---\n---\n"
    lines = []
    found = False
    for line in text.splitlines():
        if line.startswith(f"{key}:"):
            lines.append(f"{key}: {value}")
            found = True
        else:
            lines.append(line)
    if not found:
        lines.insert(1, f"{key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_inbox(root: Path, text: str, source: str = "telegram") -> Path:
    ensure_vault(root)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = root / "inbox" / f"{day}.md"
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    block = f"\n## {ts} · {source}\n\n{text.strip()}\n"
    if not path.exists():
        path.write_text(f"# Inbox {day}\n", encoding="utf-8")
    with path.open("a", encoding="utf-8") as f:
        f.write(block)
    return path


def append_session(root: Path, session_slug: str, text: str) -> Path:
    ensure_vault(root)
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in session_slug.lower()).strip("-")
    if not safe:
        safe = "untitled"
    path = root / "sessions" / f"{safe}.md"
    ts = datetime.now(timezone.utc).isoformat()
    if not path.exists():
        path.write_text(
            f"---\ntitle: {session_slug}\nstatus: open\ncreated: {ts}\n---\n\n# {session_slug}\n",
            encoding="utf-8",
        )
    with path.open("a", encoding="utf-8") as f:
        f.write(f"\n### {ts}\n\n{text.strip()}\n")
    return path


def close_session(root: Path, session_slug: str) -> Path | None:
    ensure_vault(root)
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in session_slug.lower()).strip("-")
    path = root / "sessions" / f"{safe}.md"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    text = text.replace("status: open", "status: closed", 1)
    path.write_text(text, encoding="utf-8")
    return path


def list_open_sessions(root: Path) -> list[Path]:
    ensure_vault(root)
    out = []
    for p in (root / "sessions").glob("*.md"):
        head = p.read_text(encoding="utf-8", errors="ignore")[:500]
        if "status: closed" not in head:
            out.append(p)
    return out


def write_promise(root: Path, title: str, detail: str) -> Path:
    ensure_vault(root)
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in title.lower())[:60].strip("-")
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = root / "promises" / "open" / f"{ts}-{safe or 'promise'}.md"
    path.write_text(
        f"---\ntitle: {title}\nstatus: open\ncreated: {datetime.now(timezone.utc).isoformat()}\n---\n\n"
        f"# {title}\n\n{detail.strip()}\n",
        encoding="utf-8",
    )
    return path


def list_open_promises(root: Path) -> list[Path]:
    ensure_vault(root)
    return sorted((root / "promises" / "open").glob("*.md"))


def log_proactive(root: Path, reason: str, message: str) -> None:
    ensure_vault(root)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = root / "proactive" / f"{day}.md"
    ts = datetime.now(timezone.utc).isoformat()
    with path.open("a", encoding="utf-8") as f:
        f.write(f"\n## {ts}\n\n**why:** {reason}\n\n{message}\n")


def log_pattern_event(root: Path, event: str) -> None:
    ensure_vault(root)
    path = root / "patterns" / "events.md"
    ts = datetime.now(timezone.utc).isoformat()
    with path.open("a", encoding="utf-8") as f:
        f.write(f"- {ts} · {event}\n")


def recent_context(root: Path, limit_chars: int = 3000) -> str:
    ensure_vault(root)
    chunks: list[str] = []
    inbox = sorted((root / "inbox").glob("*.md"), reverse=True)[:2]
    for p in inbox:
        chunks.append(p.read_text(encoding="utf-8", errors="ignore")[-1500:])
    for p in list_open_promises(root)[:5]:
        chunks.append(p.read_text(encoding="utf-8", errors="ignore")[:800])
    text = "\n---\n".join(chunks)
    return text[-limit_chars:]
