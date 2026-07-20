"""Markdown vault I/O — per-user source of truth."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def user_root(root: Path, user_id: int) -> Path:
    return root / "users" / str(user_id)


def ensure_user_vault(root: Path, user_id: int) -> Path:
    ur = user_root(root, user_id)
    for rel in (
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
    ):
        (ur / rel).mkdir(parents=True, exist_ok=True)
    profile = ur / "profile.md"
    if not profile.exists():
        profile.write_text(
            f"---\nuser_id: {user_id}\nchat_id: \nquiet: false\n"
            f"voice: true\nproactivity: medium\ncreated: {datetime.now(timezone.utc).isoformat()}\n---\n",
            encoding="utf-8",
        )
    return ur


def ensure_vault(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "users").mkdir(exist_ok=True)
    (root / "config").mkdir(exist_ok=True)
    reg = root / "registry"
    reg.mkdir(exist_ok=True)
    prefs = root / "config" / "preferences.md"
    if not prefs.exists():
        prefs.write_text(
            "# Global preferences\n\nproactivity_level: medium\nvoice_reminders: true\n",
            encoding="utf-8",
        )


def register_user(root: Path, user_id: int, chat_id: int, username: str = "") -> None:
    ensure_vault(root)
    ensure_user_vault(root, user_id)
    path = root / "registry" / "chats.json"
    data: dict = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
    data[str(user_id)] = {
        "chat_id": chat_id,
        "username": username,
        "updated": datetime.now(timezone.utc).isoformat(),
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    # profile chat_id
    ur = user_root(root, user_id)
    prof = ur / "profile.md"
    text = prof.read_text(encoding="utf-8") if prof.exists() else ""
    if "chat_id:" in text:
        lines = []
        for line in text.splitlines():
            if line.startswith("chat_id:"):
                lines.append(f"chat_id: {chat_id}")
            else:
                lines.append(line)
        prof.write_text("\n".join(lines) + "\n", encoding="utf-8")


def list_registered_users(root: Path) -> list[dict]:
    path = root / "registry" / "chats.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    out = []
    for uid, meta in data.items():
        out.append({"user_id": int(uid), "chat_id": meta.get("chat_id"), **meta})
    return out


def append_inbox(root: Path, user_id: int, text: str, source: str = "telegram") -> Path:
    ur = ensure_user_vault(root, user_id)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = ur / "inbox" / f"{day}.md"
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    block = f"\n## {ts} · {source}\n\n{text.strip()}\n"
    if not path.exists():
        path.write_text(f"# Inbox {day}\n", encoding="utf-8")
    with path.open("a", encoding="utf-8") as f:
        f.write(block)
    return path


def append_session(root: Path, user_id: int, session_slug: str, text: str) -> Path:
    ur = ensure_user_vault(root, user_id)
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in session_slug.lower()).strip("-")
    if not safe:
        safe = "untitled"
    path = ur / "sessions" / f"{safe}.md"
    ts = datetime.now(timezone.utc).isoformat()
    if not path.exists():
        path.write_text(
            f"---\ntitle: {session_slug}\nstatus: open\ncreated: {ts}\n---\n\n# {session_slug}\n",
            encoding="utf-8",
        )
    with path.open("a", encoding="utf-8") as f:
        f.write(f"\n### {ts}\n\n{text.strip()}\n")
    return path


def close_session(root: Path, user_id: int, session_slug: str) -> Path | None:
    ur = ensure_user_vault(root, user_id)
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in session_slug.lower()).strip("-")
    path = ur / "sessions" / f"{safe}.md"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    text = text.replace("status: open", "status: closed", 1)
    path.write_text(text, encoding="utf-8")
    return path


def list_open_sessions(root: Path, user_id: int) -> list[Path]:
    ur = ensure_user_vault(root, user_id)
    out = []
    for p in (ur / "sessions").glob("*.md"):
        head = p.read_text(encoding="utf-8", errors="ignore")[:500]
        if "status: closed" not in head:
            out.append(p)
    return out


def write_promise(root: Path, user_id: int, title: str, detail: str) -> Path:
    ur = ensure_user_vault(root, user_id)
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in title.lower())[:60].strip("-")
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = ur / "promises" / "open" / f"{ts}-{safe or 'promise'}.md"
    path.write_text(
        f"---\ntitle: {title}\nstatus: open\ncreated: {datetime.now(timezone.utc).isoformat()}\n---\n\n"
        f"# {title}\n\n{detail.strip()}\n",
        encoding="utf-8",
    )
    return path


def list_open_promises(root: Path, user_id: int) -> list[Path]:
    ur = ensure_user_vault(root, user_id)
    return sorted((ur / "promises" / "open").glob("*.md"))


def log_proactive(root: Path, user_id: int, reason: str, message: str) -> None:
    ur = ensure_user_vault(root, user_id)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = ur / "proactive" / f"{day}.md"
    ts = datetime.now(timezone.utc).isoformat()
    with path.open("a", encoding="utf-8") as f:
        f.write(f"\n## {ts}\n\n**why:** {reason}\n\n{message}\n")


def log_pattern_event(root: Path, user_id: int, event: str) -> None:
    ur = ensure_user_vault(root, user_id)
    path = ur / "patterns" / "events.md"
    ts = datetime.now(timezone.utc).isoformat()
    with path.open("a", encoding="utf-8") as f:
        f.write(f"- {ts} · {event}\n")


def recent_context(root: Path, user_id: int, limit_chars: int = 3000) -> str:
    ur = ensure_user_vault(root, user_id)
    chunks: list[str] = []
    # latest inbox
    inbox = sorted((ur / "inbox").glob("*.md"), reverse=True)[:2]
    for p in inbox:
        chunks.append(p.read_text(encoding="utf-8", errors="ignore")[-1500:])
    for p in list_open_promises(root, user_id)[:5]:
        chunks.append(p.read_text(encoding="utf-8", errors="ignore")[:800])
    text = "\n---\n".join(chunks)
    return text[-limit_chars:]
