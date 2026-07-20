"""Listen mode — Telegram-as-Pocket continuous audio session."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from farzana.services import vault as vault_io


def _state_path(root: Path) -> Path:
    vault_io.ensure_vault(root)
    return root / "config" / "listen.json"


def get_listen_state(root: Path) -> dict | None:
    path = _state_path(root)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not data.get("active"):
        return None
    return data


def start_listen(root: Path, session_name: str) -> str:
    vault_io.ensure_vault(root)
    name = (session_name or "listen").strip() or "listen"
    # open/append session header
    vault_io.append_session(
        root,
        name,
        f"(listen mode started {datetime.now(timezone.utc).isoformat()} — send long voice/audio; /stop or /close when done)",
    )
    path = _state_path(root)
    path.write_text(
        json.dumps(
            {
                "active": True,
                "session": name,
                "started": datetime.now(timezone.utc).isoformat(),
                "chunks": 0,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return name


def stop_listen(root: Path) -> str | None:
    state = get_listen_state(root)
    path = _state_path(root)
    if path.exists():
        path.write_text(
            json.dumps({"active": False, "stopped": datetime.now(timezone.utc).isoformat()}, indent=2),
            encoding="utf-8",
        )
    return (state or {}).get("session")


def record_chunk(root: Path, transcript: str) -> tuple[str, int]:
    """Append transcript to active listen session. Returns (session_name, chunk_n)."""
    state = get_listen_state(root)
    if not state:
        raise RuntimeError("listen mode is not active")
    session = state["session"]
    n = int(state.get("chunks") or 0) + 1
    vault_io.append_session(
        root,
        session,
        f"[listen chunk {n} · {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}]\n\n{transcript.strip()}",
    )
    state["chunks"] = n
    state["updated"] = datetime.now(timezone.utc).isoformat()
    _state_path(root).write_text(json.dumps(state, indent=2), encoding="utf-8")
    return session, n
